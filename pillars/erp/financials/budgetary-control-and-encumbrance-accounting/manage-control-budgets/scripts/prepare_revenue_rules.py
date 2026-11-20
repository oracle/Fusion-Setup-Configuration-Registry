#!/usr/bin/env python3
"""Validate normalized Revenue Funding Rule inputs and map evidenced CSV rows.

The caller must finish Control Budget validation and current-target lookup/COA
resolution before invoking this local helper. Lookup codes and COA roles are
supplied evidence, never inferred here. This module makes no external calls,
creates no ZIP, and performs no import. Specific value/account membership and
scenario existence are explicitly deferred to Fusion.

Input: {controlBudget: {name, sourceBudgetType, allowRevenueFundingFlag,
budgetSegments: [ordered names or {segmentName: ...}]}, revenueFundingRules:
[{ruleName, description?, enabledFlag?, maximumFunding: {type, lookupCode,
amount?, budgetScenario?}, minimumRevenue: {...}, fundingTargets:
[{budgetAccount, fundingPercentage}], revenueSource: {ledgerName, coaSegments:
[{segmentName, segmentColumnName, segmentLabels: [...], sequenceNumber}], segmentFilters:
[{segmentColumnName, selection: "All" | "Specific", values?: [strings]}]}}]}.

Both type selections are explicit business meanings. Each lookupCode must be
resolved from ORA_XCC_REVENUE_LIMIT_TYPE by the active resolver; this helper
checks presence, not remote membership. Source metadata must contain exact
GL_BALANCING and GL_ACCOUNT labels, as arrays or bracketed comma-separated
BOSS label-token strings. Missing filters default to All except
those labeled segments, which require Specific user values.
Source sequenceNumber values must be positive, unique integers or integer strings.
Source conditions and Detail groups use ascending numeric sequenceNumber order;
entered value order and returned columns are preserved, with funding targets last.
Amounts and percentages supplied to the Python API must be decimal text,
integers, or Decimal objects; binary floats are rejected because their original
decimal text is lost. The CLI retains fractional/exponent JSON number tokens
without a float conversion, including trailing zeros and exponent spelling.
"""

from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
from pathlib import Path
import re
from typing import Any, Mapping


RULE_CSV = "ORA_XCC_CONTROL_BUDGET_REVENUE_FUNDING_RULE.csv"
CONDITION_CSV = "ORA_XCC_CONTROL_BUDGET_REVENUE_FUNDING_RULE_CONDITION.csv"
DETAIL_CSV = "ORA_XCC_CONTROL_BUDGET_REVENUE_FUNDING_RULE_DETAIL.csv"
HEADERS = {
    RULE_CSV: (
        "ORA_XCC_CONTROL_BUDGET.Name", "RuleName", "Description", "EnabledFlag",
        "MaxFundingBudgetScenario", "MaxFundingFixedAmount", "MaxFundingLimitTypeCode",
        "MinRevBudgetScenario", "MinRevFixedAmount", "MinRevThresholdTypeCode",
        "RevFundingSourceLedgerName",
    ),
    CONDITION_CSV: (
        "ORA_XCC_CONTROL_BUDGET.Name",
        "ORA_XCC_CONTROL_BUDGET_REVENUE_FUNDING_RULE.RuleName",
        "FilterConditionCode", "ApplicableToAllValuesFlag",
    ),
    DETAIL_CSV: (
        "ORA_XCC_CONTROL_BUDGET.Name",
        "ORA_XCC_CONTROL_BUDGET_REVENUE_FUNDING_RULE.RuleName",
        "ORA_XCC_CONTROL_BUDGET_REVENUE_FUNDING_RULE_CONDITION.FilterConditionCode",
        "RevFundingPercentage", "FilterConditionValue",
    ),
}
TARGET_CODE = "TARGET_FUNDING_BUDGET_ACCOUNT"
ROLE_LABELS = ("GL_BALANCING", "GL_ACCOUNT")
MAX_TYPES = {"Fixed amount", "Revenue estimate", "Unlimited"}
MIN_TYPES = {"Fixed amount", "Revenue estimate", "No minimum"}
_UNSET = object()


class RevenueInputError(ValueError):
    """The top-level normalized input does not satisfy the helper contract."""


class _JsonDecimalToken:
    """Keep a JSON number's spelling without turning nonnumeric fields into text."""

    def __init__(self, token: str):
        self.token = token

    def __str__(self) -> str:
        return self.token


def _json_default(value: Any) -> str:
    if isinstance(value, _JsonDecimalToken):
        return value.token
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _supplied(value: Any) -> bool:
    return value is not None and value != ""


def _decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal, _JsonDecimalToken)):
        return None
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def _csv_number(value: Any) -> str:
    # Preserve textual precision; never convert account/segment values to numbers.
    return str(value)


def _sequence_number(value: Any) -> int | None:
    """Normalize BOSS ordering metadata without deriving it from column names."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        raw = value.strip()
        if not re.fullmatch(r"[0-9]+", raw):
            return None
        try:
            number = int(raw)
        except ValueError:
            return None
    elif isinstance(value, int):
        number = value
    else:
        return None
    return number if number > 0 else None


def _segment_labels(value: Any) -> list[str] | None:
    """Accept normalized arrays or the BOSS bracketed label-token format."""
    if isinstance(value, list):
        return list(value) if all(_text(label) for label in value) else None
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return None
    contents = raw[1:-1].strip()
    if not contents:
        return []
    labels = [label.strip() for label in contents.split(",")]
    if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", label) for label in labels):
        return None
    return labels


def _supplied_issue_value(value: Any) -> str | None:
    """Use the string/null transport contract without erasing invalid inputs."""
    if isinstance(value, _JsonDecimalToken):
        return value.token
    if isinstance(value, str) or value is None:
        return value
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, default=str)
    except (ValueError, TypeError):
        return str(value)


class _Checks:
    def __init__(self, rule_name: str, prefix: str):
        self.rule_name = rule_name
        self.prefix = prefix
        self.items: list[dict[str, Any]] = []

    def add(self, identifier: str, section: str, field: str, label: str,
            messages: list[str | dict[str, Any]] | None = None, *, prerequisites: list[str] | None = None,
            reason: str | None = None, deferral: str | None = None,
            supplied_value: Any = _UNSET) -> str:
        check_id = f"{self.prefix}.{identifier}"
        path = field if field.startswith("controlBudget.") else f"{self.prefix}.{field}"
        status = "failed" if messages else "passed"
        entry: dict[str, Any] = {
            "id": check_id, "section": section, "path": path, "check": label,
            "status": status, "ruleName": self.rule_name,
            "prerequisites": prerequisites or [],
        }
        if reason:
            entry.update(status="not_evaluated", reason=reason)
        elif deferral:
            entry.update(
                status="deferred_to_fusion", deferralId=deferral,
                basis="Membership/existence is validated by Fusion import; "
                      "only required inputs and local structure are checked here.",
            )
        elif messages:
            entry["issues"] = []
            for message in messages:
                issue = dict(message) if isinstance(message, dict) else {"message": message}
                issue.setdefault("path", path)
                issue.setdefault("failureClass", "input validation")
                issue.setdefault("ruleName", self.rule_name)
                issue.setdefault("recommendedAction", "Correct this field using the required input contract and regenerate validation.")
                if "suppliedValue" in issue:
                    issue["suppliedValue"] = _supplied_issue_value(issue["suppliedValue"])
                elif supplied_value is not _UNSET:
                    issue["suppliedValue"] = _supplied_issue_value(supplied_value)
                entry["issues"].append(issue)
        self.items.append(entry)
        return check_id

    def passed(self, identifier: str) -> bool:
        return next(item["status"] for item in self.items if item["id"] == identifier) == "passed"

    @property
    def blocked(self) -> bool:
        return any(item["status"] in {"failed", "not_evaluated"} for item in self.items)


def _limit(raw: Any, *, maximum: bool, checks: _Checks) -> dict[str, Any]:
    field = "maximumFunding" if maximum else "minimumRevenue"
    allowed = MAX_TYPES if maximum else MIN_TYPES
    settings = dict(raw) if isinstance(raw, dict) else {}
    selected = settings.get("type")
    canonical = {choice.casefold(): choice for choice in allowed}
    if isinstance(selected, str):
        selected = canonical.get(selected.strip().casefold(), selected)
        settings["type"] = selected
    type_label = "Maximum Funding Limit Type" if maximum else "Minimum Revenue Threshold Type"
    conditional_label = "Maximum Funding conditional fields" if maximum else "Minimum Revenue conditional fields"
    selected_id = checks.add(
        field + ".type", "rule_header", field + ".type", type_label,
        [] if isinstance(selected, str) and selected in allowed else
        ["Supply an explicit supported type: " + ", ".join(sorted(allowed)) + "."],
        supplied_value=settings.get("type"),
    )
    checks.add(
        field + ".lookup", "rule_header", field + ".lookupCode", type_label + " Code",
        [] if _text(settings.get("lookupCode")) else
        ["A current-target LookupCode resolved from ORA_XCC_REVENUE_LIMIT_TYPE is required."],
        supplied_value=settings.get("lookupCode"),
    )
    if not checks.passed(selected_id):
        checks.add(field + ".conditional", "rule_header", field,
                   conditional_label, prerequisites=[selected_id],
                   reason="Conditional fields require a valid explicit type.")
        return settings
    errors = []
    def field_issue(name: str, message: str) -> dict[str, Any]:
        return {"path": f"{checks.prefix}.{field}.{name}", "message": message,
                "suppliedValue": settings.get(name)}
    if selected == "Fixed amount":
        amount = _decimal(settings.get("amount"))
        if amount is None or amount <= 0:
            errors.append(field_issue("amount", "Fixed amount requires a finite numeric amount greater than zero."))
        if _supplied(settings.get("budgetScenario")):
            errors.append(field_issue("budgetScenario", "Budget Scenario must be omitted when the type is Fixed amount."))
    elif selected == "Revenue estimate":
        if not _text(settings.get("budgetScenario")):
            errors.append(field_issue("budgetScenario", "Revenue estimate requires a nonblank Budget Scenario."))
        if _supplied(settings.get("amount")):
            errors.append(field_issue("amount", "Fixed amount must be omitted when the type is Revenue estimate."))
    else:
        for name in ("amount", "budgetScenario"):
            if _supplied(settings.get(name)):
                errors.append(field_issue(name, "This type requires both amount and Budget Scenario to be omitted."))
    checks.add(field + ".conditional", "rule_header", field,
               conditional_label, errors, prerequisites=[selected_id])
    if selected == "Revenue estimate" and _text(settings.get("budgetScenario")):
        # Scenario existence is independent of unrelated conflicting amount input.
        checks.add(field + ".scenario_membership", "rule_header", field + ".budgetScenario",
                   "Budget Scenario existence", deferral="budget_scenario_membership")
    return settings


def _targets(rule: Mapping[str, Any], budget: Mapping[str, Any], checks: _Checks) -> list[dict[str, Any]]:
    section = "funding_targets"
    raw_segments = budget.get("budgetSegments")
    segment_names = []
    segment_errors = []
    if not isinstance(raw_segments, list) or not raw_segments:
        segment_errors.append("Resolved ordered parent budget segments are required.")
    else:
        for item in raw_segments:
            name = item.get("segmentName", item.get("name")) if isinstance(item, dict) else item
            if not _text(name):
                segment_errors.append("Every ordered budget segment requires a nonblank name.")
            else:
                segment_names.append(name)
        if len(set(segment_names)) != len(segment_names):
            segment_errors.append("Ordered budget segment identities must be unique.")
    segments_id = checks.add("budget_segments", section, "controlBudget.budgetSegments",
                             "Parent budget segment structure", segment_errors)
    raw = rule.get("fundingTargets")
    present = isinstance(raw, list) and bool(raw)
    targets_id = checks.add("targets", section, "fundingTargets", "Funding targets",
                            [] if present else ["At least one funding target is required."])
    if not present:
        return []
    normalized = []
    numeric_ids = []
    numbers: list[Decimal] = []
    seen_accounts: set[str] = set()
    for index, item in enumerate(raw):
        target = item if isinstance(item, dict) else {}
        field = f"fundingTargets.{index}"
        account = target.get("budgetAccount")
        account_errors = [] if _text(account) else ["Budget Account is required as nonblank text."]
        if _text(account) and account in seen_accounts:
            account_errors.append("Duplicate target Budget Account.")
        if _text(account):
            seen_accounts.add(account)
        account_id = checks.add(f"target.{index}.account", section, field + ".budgetAccount",
                                "Target Budget Account", account_errors, supplied_value=account)
        shape_errors = []
        prerequisites = [segments_id, account_id]
        if all(checks.passed(identifier) for identifier in prerequisites):
            components = account.split("-")
            if len(components) != len(segment_names) or not all(part.strip() for part in components):
                shape_errors.append("Budget Account must have one nonblank component per ordered "
                                    "parent budget segment, separated by '-'.")
            shape_id = checks.add(f"target.{index}.shape", section, field + ".budgetAccount",
                                  "Target account combination shape", shape_errors,
                                  prerequisites=prerequisites, supplied_value=account)
            if checks.passed(shape_id):
                checks.add(f"target.{index}.membership", section, field + ".budgetAccount",
                           "Target account membership", prerequisites=[shape_id],
                           deferral="target_budget_account_membership")
        else:
            checks.add(f"target.{index}.shape", section, field + ".budgetAccount",
                       "Target account combination shape", prerequisites=prerequisites,
                       reason="Account shape requires an account and resolved parent segments.")
        number = _decimal(target.get("fundingPercentage"))
        number_id = checks.add(f"target.{index}.numeric", section, field + ".fundingPercentage",
                               "Funding percentage numeric input",
                               [] if number is not None else ["Funding Percentage must be finite numeric input."],
                               supplied_value=target.get("fundingPercentage"))
        numeric_ids.append(number_id)
        if number is not None:
            numbers.append(number)
            checks.add(f"target.{index}.positive", section, field + ".fundingPercentage",
                       "Funding percentage positive", [] if number > 0 else
                       ["Funding Percentage must be greater than zero."], prerequisites=[number_id],
                       supplied_value=target.get("fundingPercentage"))
        else:
            checks.add(f"target.{index}.positive", section, field + ".fundingPercentage",
                       "Funding percentage positive", prerequisites=[number_id],
                       reason="Percentage bounds require finite numeric input.")
        normalized.append(target)
    if all(checks.passed(identifier) for identifier in numeric_ids):
        checks.add("targets.total", section, "fundingTargets", "Funding percentage total",
                   [] if sum((Fraction(number) for number in numbers), Fraction(0)) == 100 else
                   ["Funding percentages must total exactly 100%."],
                   prerequisites=[targets_id] + numeric_ids,
                   supplied_value=[target.get("fundingPercentage") for target in normalized])
    else:
        checks.add("targets.total", section, "fundingTargets", "Funding percentage total",
                   prerequisites=[targets_id] + numeric_ids,
                   reason="Percentage total requires numeric input for every target.")
    return normalized


def _source(rule: Mapping[str, Any], checks: _Checks) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    section = "revenue_source_segments"
    raw = rule.get("revenueSource")
    source = raw if isinstance(raw, dict) else {}
    checks.add("source.ledger", section, "revenueSource.ledgerName", "Revenue-source ledger",
               [] if _text(source.get("ledgerName")) else ["Resolved revenue-source Ledger Name is required."])
    metadata = source.get("coaSegments")
    metadata_errors = []
    by_column: dict[str, dict[str, Any]] = {}
    seen_sequences: set[int] = set()
    if not isinstance(metadata, list) or not metadata:
        metadata_errors.append("All resolved source COA segments and their role labels are required.")
    else:
        for index, item in enumerate(metadata):
            if not isinstance(item, dict):
                metadata_errors.append(f"COA segment {index + 1} must be an object.")
                continue
            sequence = _sequence_number(item.get("sequenceNumber"))
            sequence_issue = None
            if sequence is None:
                sequence_issue = "Source COA sequenceNumber must be a positive integer or an integer string."
            elif sequence in seen_sequences:
                sequence_issue = "Source COA sequenceNumber must be unique within the selected source COA."
            else:
                seen_sequences.add(sequence)
            if sequence_issue:
                metadata_errors.append({
                    "path": f"{checks.prefix}.revenueSource.coaSegments.{index}.sequenceNumber",
                    "message": sequence_issue,
                    "suppliedValue": item.get("sequenceNumber"),
                    "recommendedAction": "Retain the valid, unique sequenceNumber returned by the selected source COA lookup.",
                })
            column = item.get("segmentColumnName")
            if not _text(column) or not _text(item.get("segmentName")):
                metadata_errors.append(f"COA segment {index + 1} requires name and segmentColumnName.")
                continue
            if column == TARGET_CODE or column in by_column:
                metadata_errors.append(f"COA segment {index + 1} has a duplicate/reserved column identity.")
                continue
            labels = _segment_labels(item.get("segmentLabels"))
            if labels is None:
                metadata_errors.append(f"COA segment {index + 1} requires a segmentLabels array "
                                       "or bracketed BOSS label-token string.")
            elif len(set(labels)) != len(labels):
                metadata_errors.append(f"COA segment {index + 1} contains duplicate labels.")
            by_column[column] = {**item, "segmentLabels": labels, "sequenceNumber": sequence}
    if not metadata_errors:
        by_column = dict(sorted(by_column.items(), key=lambda pair: pair[1]["sequenceNumber"]))
    metadata_id = checks.add("source.metadata", section, "revenueSource.coaSegments",
                             "Revenue-source COA metadata", metadata_errors)
    role_errors = []
    roles: set[str] = set()
    if checks.passed(metadata_id):
        role_columns: dict[str, list[str]] = {}
        for role in ROLE_LABELS:
            columns = [column for column, item in by_column.items() if role in item["segmentLabels"]]
            role_columns[role] = columns
            if len(columns) != 1:
                role_errors.append(f"Exactly one source COA segment must carry {role}.")
            roles.update(columns)
        if (len(role_columns["GL_BALANCING"]) == len(role_columns["GL_ACCOUNT"]) == 1 and
                role_columns["GL_BALANCING"][0] == role_columns["GL_ACCOUNT"][0]):
            role_errors.append("Primary Balancing and Natural Account roles must identify distinct source COA segments.")
        roles_id = checks.add("source.roles", section, "revenueSource.coaSegments",
                              "Revenue-source accounting roles", role_errors,
                              prerequisites=[metadata_id])
    else:
        roles_id = checks.add("source.roles", section, "revenueSource.coaSegments",
                              "Revenue-source accounting roles", prerequisites=[metadata_id],
                              reason="Role identification requires complete valid COA metadata.")
    raw_filters = source.get("segmentFilters", [])
    filters_errors = [] if isinstance(raw_filters, list) else ["segmentFilters must be an array."]
    filters_id = checks.add("source.filters", section, "revenueSource.segmentFilters",
                            "Revenue-source filter collection", filters_errors)
    supplied: dict[str, dict[str, Any]] = {}
    if isinstance(raw_filters, list):
        for index, raw_filter in enumerate(raw_filters):
            item = raw_filter if isinstance(raw_filter, dict) else {}
            column = item.get("segmentColumnName")
            errors = []
            if not _text(column):
                errors.append("Each source filter requires segmentColumnName.")
            elif column in supplied:
                errors.append("Duplicate source segment filter.")
            else:
                supplied[column] = item
            if not isinstance(item.get("selection"), str) or item["selection"] not in {"All", "Specific"}:
                errors.append({"path": f"{checks.prefix}.revenueSource.segmentFilters.{index}.selection",
                               "message": "Source selection must be explicitly All or Specific.",
                               "suppliedValue": item.get("selection")})
            values = item.get("values", [])
            if not isinstance(values, list):
                errors.append({"path": f"{checks.prefix}.revenueSource.segmentFilters.{index}.values",
                               "message": "Specific values must be an array of nonblank text; preserve leading zeros.",
                               "suppliedValue": values})
            else:
                for value_index, value in enumerate(values):
                    if not _text(value):
                        errors.append({
                            "path": f"{checks.prefix}.revenueSource.segmentFilters.{index}.values.{value_index}",
                            "message": "Each supplied Specific value must be nonblank text; preserve leading zeros.",
                            "suppliedValue": value,
                            "recommendedAction": "Supply nonblank text for this Specific value, or remove the invalid entry while retaining at least one value.",
                        })
                if item.get("selection") == "Specific" and not values:
                    errors.append("Specific selection requires at least one supplied value.")
                elif item.get("selection") == "All" and values:
                    errors.append("All selection must not include Specific values.")
            checks.add(f"source.filter.{index}.input", section,
                       f"revenueSource.segmentFilters.{index}", "Source filter input", errors)
            if checks.passed(metadata_id) and _text(column):
                checks.add(f"source.filter.{index}.identity", section,
                           f"revenueSource.segmentFilters.{index}.segmentColumnName",
                           "Source filter COA identity", [] if column in by_column else
                           ["Source filter segmentColumnName is absent from the source COA."],
                           prerequisites=[metadata_id])
    normalized = []
    dependencies = [metadata_id, roles_id, filters_id]
    if not all(checks.passed(identifier) for identifier in dependencies):
        checks.add("source.coverage", section, "revenueSource.segmentFilters",
                   "All source COA segment conditions", prerequisites=dependencies,
                   reason="Condition completion requires valid COA metadata, roles, and filter collection.")
        return source, normalized
    for index, column in enumerate(by_column):
        item = supplied.get(column, {"segmentColumnName": column,
                                     "selection": "Specific" if column in roles else "All", "values": []})
        errors = []
        selection = item.get("selection")
        values = item.get("values", [])
        if column in roles and selection != "Specific":
            errors.append("Primary Balancing and Natural Account segments must use Specific values.")
        if selection == "Specific" and (not isinstance(values, list) or not values or
                                         not all(_text(value) for value in values)):
            errors.append("Specific selection requires at least one nonblank supplied text value.")
        checks.add(f"source.segment.{index}", section,
                   f"revenueSource.segmentFilters.{column}",
                   "Source segment selection", errors, prerequisites=dependencies,
                   supplied_value=selection)
        if selection == "Specific" and isinstance(values, list) and values and all(_text(v) for v in values):
            checks.add(f"source.segment.{index}.membership", section,
                       f"revenueSource.segmentFilters.{column}.values", "Specific segment value membership",
                       deferral="specific_segment_value_membership")
        normalized.append({"segmentColumnName": column, "selection": selection, "values": values})
    checks.add("source.coverage", section, "revenueSource.segmentFilters",
               "All source COA segment conditions", prerequisites=dependencies)
    return source, normalized


def _rows(budget: Mapping[str, Any], rule: Mapping[str, Any], maximum: Mapping[str, Any],
          minimum: Mapping[str, Any], source: Mapping[str, Any], filters: list[dict[str, Any]],
          targets: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    rows: dict[str, list[dict[str, str]]] = {name: [] for name in HEADERS}
    budget_name = budget["name"]
    rule_name = rule["ruleName"]
    values = [
        budget_name, rule_name, rule.get("description", ""), rule.get("enabledFlag", "Y"),
        maximum.get("budgetScenario", "") if maximum["type"] == "Revenue estimate" else "",
        _csv_number(maximum["amount"]) if maximum["type"] == "Fixed amount" else "",
        maximum["lookupCode"],
        minimum.get("budgetScenario", "") if minimum["type"] == "Revenue estimate" else "",
        _csv_number(minimum["amount"]) if minimum["type"] == "Fixed amount" else "",
        minimum["lookupCode"], source["ledgerName"],
    ]
    rows[RULE_CSV].append(dict(zip(HEADERS[RULE_CSV], values)))
    for condition in filters + [{"segmentColumnName": TARGET_CODE, "selection": "Specific"}]:
        code = condition["segmentColumnName"]
        all_values = condition["selection"] == "All"
        rows[CONDITION_CSV].append(dict(zip(HEADERS[CONDITION_CSV],
                                           [budget_name, rule_name, code, "Y" if all_values else "N"])))
        if code == TARGET_CODE:
            details = [(target["budgetAccount"], _csv_number(target["fundingPercentage"])) for target in targets]
        else:
            details = [] if all_values else [(value, "") for value in condition["values"]]
        for value, percentage in details:
            rows[DETAIL_CSV].append(dict(zip(HEADERS[DETAIL_CSV],
                                             [budget_name, rule_name, code, percentage, value])))
    return rows


def prepare_revenue_rules(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return gate-compatible rule checks and CSV rows, withholding all rows on failure."""
    if not isinstance(payload, Mapping):
        raise RevenueInputError("Input must be an object.")
    budget_raw = payload.get("controlBudget")
    budget = budget_raw if isinstance(budget_raw, dict) else {}
    raw_rules = payload.get("revenueFundingRules")
    if not isinstance(raw_rules, list):
        raise RevenueInputError("revenueFundingRules must be an array.")
    counts = Counter(rule.get("ruleName") for rule in raw_rules
                     if isinstance(rule, dict) and _text(rule.get("ruleName")))
    prepared = []
    rows: dict[str, list[dict[str, str]]] = {name: [] for name in HEADERS}
    for index, raw_rule in enumerate(raw_rules):
        rule = raw_rule if isinstance(raw_rule, dict) else {}
        rule_name = rule.get("ruleName") if _text(rule.get("ruleName")) else f"<rule {index + 1}>"
        checks = _Checks(rule_name, f"revenueFundingRules.{index}")
        checks.add("parent.name", "rule_header", "controlBudget.name", "Parent Control Budget identity",
                   [] if _text(budget.get("name")) else ["Resolved parent Control Budget Name is required."])
        eligibility = []
        if budget.get("sourceBudgetType") != "Other":
            eligibility.append("Revenue Rules require Source Budget Type Other.")
        if budget.get("allowRevenueFundingFlag") != "Y":
            eligibility.append("Revenue Rules require Allow Funding from Revenue enabled (Y).")
        checks.add("eligibility", "rule_header", "controlBudget", "Revenue Rule eligibility", eligibility)
        checks.add("name", "rule_header", "ruleName", "Revenue Rule Name",
                   [] if _text(rule.get("ruleName")) else ["Revenue Funding Rule Name is mandatory."],
                   supplied_value=rule.get("ruleName"))
        checks.add("identity", "rule_header", "ruleName", "Revenue Rule identity uniqueness",
                   ["Duplicate Revenue Rule Name within the parent budget."] if counts.get(rule_name, 0) > 1 else [])
        checks.add("description", "rule_header", "description", "Revenue Rule Description",
                   [] if isinstance(rule.get("description", ""), str) else ["Description must be text when supplied."],
                   supplied_value=rule.get("description"))
        checks.add("enabled", "rule_header", "enabledFlag", "Revenue Rule EnabledFlag",
                   [] if isinstance(rule.get("enabledFlag", "Y"), str) and
                   rule.get("enabledFlag", "Y") in {"Y", "N"} else ["EnabledFlag must be Y or N."],
                   supplied_value=rule.get("enabledFlag"))
        maximum = _limit(rule.get("maximumFunding"), maximum=True, checks=checks)
        minimum = _limit(rule.get("minimumRevenue"), maximum=False, checks=checks)
        checks.add("estimate_combination", "rule_header", "maximumFunding.type",
                   "Revenue estimate combination", ["Maximum and minimum cannot both use Revenue estimate."]
                   if maximum.get("type") == minimum.get("type") == "Revenue estimate" else [])
        targets = _targets(rule, budget, checks)
        source, filters = _source(rule, checks)
        prepared.append({"ruleName": rule_name, "status": "blocked" if checks.blocked else "ready",
                         "checks": checks.items})
        if not checks.blocked:
            mapped = _rows(budget, rule, maximum, minimum, source, filters, targets)
            for name in rows:
                rows[name].extend(mapped[name])
    blocked = any(rule["status"] == "blocked" for rule in prepared)
    if blocked:
        rows = {name: [] for name in HEADERS}
    return {
        "controlBudget": budget.get("name", ""), "status": "blocked" if blocked else "ready",
        "packageReady": not blocked, "revenueFundingRules": prepared, "csvRows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, type=Path, help="Normalized resolved JSON input")
    parser.add_argument("--output", required=True, type=Path, help="New local JSON check and row-mapping result (no overwrite)")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8-sig"), parse_float=_JsonDecimalToken)
        result = prepare_revenue_rules(payload)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default) + "\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Revenue preparation failed: {exc}\n")
    return 0 if result["packageReady"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
