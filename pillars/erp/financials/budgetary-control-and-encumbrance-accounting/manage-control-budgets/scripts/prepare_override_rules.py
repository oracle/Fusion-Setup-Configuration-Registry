#!/usr/bin/env python3
"""Prepare Override Rule checks and evidenced CSV rows without external calls.

Input: {controlBudget: {name, fvTypeCode: "ORA_CONSUMPTION",
allowOverridesFlag: "Y", maximumOverrideAmount?}, overrideRules: [{ruleName,
description?, enabledFlag? (defaults Y), overrideType: {lookupCode, meaning?},
amount?, transactionTypes: {selection: "All" | "Specific", values?:
[{lookupCode, meaning?}]}, journalSources?: {selection, values?: [strings]},
journalCategories?: {selection, values?: [strings]}, userAssignments: [strings]}]}.

The active workflow resolves override/transaction lookup codes before this helper.
This helper supports ORA_CONSUMPTION only. Journal and assigned-user identities,
membership, exclusions and duplicate business values are not validated locally;
supplied strings are preserved in order. Required user assignment and collection
shape are checked. No ZIP, browser, lookup or import is performed.

Specific selection of all five distinct permitted transaction types normalizes
to the source model's All state: Y and no transaction child rows. The requested
selection and lookup codes remain in check evidence.

The rule-versus-header cap comparison intentionally reproduces source Java
BigDecimal.intValue(): truncate fractions toward zero, then retain signed low
32 bits. Positivity uses exact Decimal comparison. CSV numbers retain supplied
text, so source-compatible cap comparisons do not round or rewrite amounts.
Amounts supplied to the Python API must be decimal text, integers, or Decimal
objects; binary floats are rejected because their original decimal text is lost.
The CLI retains fractional/exponent JSON number tokens without a float conversion.

Specific sources with All categories use an actual empty JeCategoryCode, evidenced
by same-task FSM readback. The model's single-space sentinel is not a CSV marker.
"""

from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from typing import Any, Mapping


RULE_CSV = "ORA_XCC_CONTROL_BUDGET_OVERRIDE_RULE.csv"
TRANSACTION_CSV = "ORA_XCC_CONTROL_BUDGET_OVERRIDE_RULE_TRANSACTION_TYPE.csv"
JOURNAL_CSV = "ORA_XCC_CONTROL_BUDGET_OVERRIDE_RULE_JOURNAL.csv"
APPROVER_CSV = "ORA_XCC_CONTROL_BUDGET_OVERRIDE_RULE_APPROVER.csv"
PARENT_KEY = "ORA_XCC_CONTROL_BUDGET.Name"
RULE_KEY = "ORA_XCC_CONTROL_BUDGET_OVERRIDE_RULE.OverrideName"
HEADERS = {
    RULE_CSV: (PARENT_KEY, "OverrideName", "Description", "OverrideTypeCode",
               "OverrideAmount", "EnabledFlag", "AllTransactionTypesFlag",
               "AllJournalSourcesFlag", "AllJournalCategoriesFlag"),
    TRANSACTION_CSV: (PARENT_KEY, RULE_KEY, "TransactionTypeCode"),
    JOURNAL_CSV: (PARENT_KEY, RULE_KEY, "JeSourceCode", "JeCategoryCode"),
    APPROVER_CSV: (PARENT_KEY, RULE_KEY, "UserName"),
}
OVERRIDE_TYPES = {"INSUFFICIENT_FUNDS", "CLOSED_PERIOD"}
TRANSACTION_TYPES = {"GL_JOURNAL", "INVOICE", "PURCHASE_ORDER", "REQUISITION", "SLA_JOURNAL"}
JOURNAL_TYPES = {"GL_JOURNAL", "SLA_JOURNAL"}
_UNSET = object()


class OverrideInputError(ValueError):
    """Malformed top-level preparation input."""


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


def java_int_value(value: Decimal) -> int:
    """Return Java BigDecimal.intValue without allocating enormous integers."""
    if not value.is_finite():
        raise ValueError("Java intValue comparison requires a finite Decimal.")
    sign, digits, exponent = value.as_tuple()
    modulus = 1 << 32
    integral_digits = digits if exponent >= 0 else digits[:max(0, len(digits) + exponent)]
    result = 0
    for digit in integral_digits:
        result = (result * 10 + digit) % modulus
    if exponent > 0:
        result = result * pow(10, exponent, modulus) % modulus
    if sign:
        result = (-result) % modulus
    return result if result < (1 << 31) else result - modulus


def _issue_value(value: Any) -> str | None:
    if isinstance(value, _JsonDecimalToken):
        return value.token
    if isinstance(value, str) or value is None:
        return value
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, default=str)
    except (ValueError, TypeError):
        return str(value)


class _Checks:
    def __init__(self, name: str, prefix: str):
        self.name, self.prefix = name, prefix
        self.items: list[dict[str, Any]] = []

    def add(self, identifier: str, section: str, field: str, label: str,
            errors: list[str] | None = None, *, prerequisites: list[str] | None = None,
            reason: str | None = None, deferral: str | None = None,
            supplied: Any = _UNSET, evidence: Mapping[str, Any] | None = None) -> str:
        identifier = f"{self.prefix}.{identifier}"
        path = field if field.startswith("controlBudget.") else f"{self.prefix}.{field}"
        check: dict[str, Any] = {
            "id": identifier, "section": section, "path": path, "check": label,
            "status": "failed" if errors else "passed", "ruleName": self.name,
            "prerequisites": prerequisites or [],
        }
        if evidence is not None:
            check["evidence"] = dict(evidence)
        if reason:
            check.update(status="not_evaluated", reason=reason)
        elif deferral:
            check.update(status="deferred_to_fusion", deferralId=deferral,
                         basis="Business identity, membership, exclusions and duplicate-value acceptance "
                               "are validated by Fusion import; supplied strings remain unchanged.")
        elif errors:
            check["issues"] = [{
                "path": path, "message": error, "ruleName": self.name,
                "failureClass": "input validation",
                "recommendedAction": "Correct the required input or supply the missing package evidence, then regenerate validation.",
                **({"suppliedValue": _issue_value(supplied)} if supplied is not _UNSET else {}),
            } for error in errors]
        self.items.append(check)
        return identifier

    def passed(self, identifier: str) -> bool:
        return next(item["status"] for item in self.items if item["id"] == identifier) == "passed"

    @property
    def blocked(self) -> bool:
        return any(item["status"] in {"failed", "not_evaluated"} for item in self.items)


def _transaction_types(rule: Mapping[str, Any], checks: _Checks) -> tuple[list[str], str]:
    raw = rule.get("transactionTypes")
    selection = raw.get("selection") if isinstance(raw, dict) else None
    values = raw.get("values", []) if isinstance(raw, dict) else []
    errors = []
    if selection not in ("All", "Specific"):
        errors.append("Select All or Specific transaction types explicitly.")
    if not isinstance(values, list):
        errors.append("Transaction type values must be an array of resolved lookup records.")
        values = []
    if selection == "All" and values:
        errors.append("All transaction types must not also supply Specific values.")
    if selection == "Specific" and not values:
        errors.append("Specific transaction types require at least one selected type.")
    selection_id = checks.add("transactions.selection", "transaction_types", "transactionTypes",
                              "Override transaction type selection", errors, supplied=raw)
    codes = []
    for index, value in enumerate(values):
        code = value.get("lookupCode") if isinstance(value, dict) else None
        code_errors = [] if isinstance(code, str) and code in TRANSACTION_TYPES else [
            "Supply an allowed current-target transaction LookupCode: " + ", ".join(sorted(TRANSACTION_TYPES)) + "."]
        if isinstance(code, str) and code in codes:
            code_errors.append("Duplicate transaction type selection.")
        checks.add(f"transactions.{index}", "transaction_types", f"transactionTypes.values.{index}.lookupCode",
                   "Override transaction type code", code_errors, supplied=code)
        if isinstance(code, str):
            codes.append(code)
    all_flag = "Y" if selection == "All" or set(codes) == TRANSACTION_TYPES else "N"
    next(item for item in checks.items if item["id"] == selection_id)["evidence"] = {
        "requestedSelection": selection, "requestedLookupCodes": codes,
        "effectiveAllTransactionTypesFlag": all_flag,
    }
    return codes, all_flag


def _journal_selection(rule: Mapping[str, Any], field: str, checks: _Checks) -> tuple[str, list[str], str]:
    raw = rule.get(field, {"selection": "All"})
    selection = raw.get("selection") if isinstance(raw, dict) else None
    values = raw.get("values", []) if isinstance(raw, dict) else []
    errors = []
    if selection not in ("All", "Specific"):
        errors.append("Journal selection must be All or Specific.")
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        errors.append("Journal values must be an array of strings; values are passed through without identity validation.")
        values = []
    if selection == "All" and values:
        errors.append("All selection must not also supply Specific journal values.")
    if selection == "Specific" and not values:
        errors.append("Specific journal selection requires a nonempty value collection.")
    identifier = checks.add(field + ".shape", "journal_conditions", field,
                            "Override journal selection shape", errors, supplied=raw)
    return selection, values, identifier


def _journals(rule: Mapping[str, Any], codes: list[str],
              all_types: str, checks: _Checks) -> tuple[str, str, list[tuple[str, str]]]:
    source_selection, sources, source_id = _journal_selection(rule, "journalSources", checks)
    category_selection, categories, category_id = _journal_selection(rule, "journalCategories", checks)
    transaction_checks = [item for item in checks.items if item["section"] == "transaction_types"]
    prerequisites = [item["id"] for item in transaction_checks] + [source_id, category_id]
    if not all(item["status"] == "passed" for item in transaction_checks) or not all(
            checks.passed(identifier) for identifier in (source_id, category_id)):
        checks.add("journals.applicability", "journal_conditions", "journalSources",
                   "Override journal applicability", prerequisites=prerequisites,
                   reason="Journal applicability requires valid transaction and journal selection shapes.")
        return "Y", "Y", []
    errors = []
    read_only = all_types == "Y" or not (set(codes) & JOURNAL_TYPES)
    if read_only and (source_selection != "All" or category_selection != "All"):
        errors.append("This transaction selection requires All journal sources and All journal categories.")
    if source_selection == "All" and category_selection != "All":
        errors.append("Specific journal categories require exactly one Specific journal source.")
    if source_selection == "Specific" and len(sources) != 1 and category_selection != "All":
        errors.append("Specific journal categories require exactly one Specific journal source.")
    applicability_id = checks.add("journals.applicability", "journal_conditions", "journalSources",
                                  "Override journal applicability", errors, prerequisites=prerequisites)
    if sources:
        checks.add("journals.source_membership", "journal_conditions", "journalSources.values",
                   "Override journal source membership", prerequisites=[source_id],
                   deferral="journal_source_membership")
    if categories:
        checks.add("journals.category_membership", "journal_conditions", "journalCategories.values",
                   "Override journal category membership", prerequisites=[category_id],
                   deferral="journal_category_membership")
    source_flag = "Y" if source_selection == "All" else "N"
    category_flag = "Y" if category_selection == "All" else "N"
    journal_rows: list[tuple[str, str]] = []
    if checks.passed(applicability_id) and source_flag == "N":
        if category_flag == "N":
            journal_rows = [(sources[0], category) for category in categories]
        else:
            checks.add("journals.category_marker", "journal_conditions", "journalCategories",
                       "Override All categories CSV representation",
                       prerequisites=[applicability_id],
                       evidence={"csvValue": "", "length": 0,
                                 "basis": "Same-task FSM readback; model single-space sentinel is not serialized.",
                                 "archiveSha256": "1d4211afb358f777d18e7e26c763a2b1cee01dff96541069e9333893b4e6dfca"})
            journal_rows = [(source, "") for source in sources]
    return source_flag, category_flag, journal_rows


def _users(rule: Mapping[str, Any], checks: _Checks) -> list[str]:
    raw = rule.get("userAssignments")
    errors = []
    if not isinstance(raw, list) or not raw:
        errors.append("Every Override Rule requires at least one assigned user.")
        values = []
    else:
        values = raw
    identifier = checks.add("users.required", "user_assignments", "userAssignments",
                            "Override user assignments", errors, supplied=raw)
    shape_ids = []
    for index, user in enumerate(values):
        shape_ids.append(checks.add(f"users.{index}.shape", "user_assignments", f"userAssignments.{index}",
                                   "Override assigned user input", [] if _text(user) else ["Assigned user must be nonblank text."],
                                   prerequisites=[identifier], supplied=user))
    if values:
        prerequisites = [identifier] + shape_ids
        if all(checks.passed(item) for item in prerequisites):
            checks.add("users.membership", "user_assignments", "userAssignments",
                       "Override assigned user membership", prerequisites=prerequisites,
                       deferral="override_user_membership")
        else:
            checks.add("users.membership", "user_assignments", "userAssignments",
                       "Override assigned user membership", prerequisites=prerequisites,
                       reason="User membership is deferred only after assignment input shape is valid.")
    return values


def _amounts(rule: Mapping[str, Any], budget: Mapping[str, Any], type_code: Any,
             type_id: str, enabled_id: str, checks: _Checks) -> None:
    raw = rule.get("amount")
    amount = _decimal(raw)
    max_raw = budget.get("maximumOverrideAmount")
    maximum = _decimal(max_raw)
    max_errors = []
    if _supplied(max_raw) and (maximum is None or maximum < 0):
        max_errors.append("A supplied MaximumOverrideAmount must be finite numeric input greater than or equal to zero.")
    max_id = checks.add("maximum.numeric", "rule_header", "controlBudget.maximumOverrideAmount",
                        "Control Budget maximum override amount", max_errors, supplied=max_raw)
    if not checks.passed(type_id):
        checks.add("amount", "rule_header", "amount", "Override amount", prerequisites=[type_id],
                   reason="Amount applicability requires a supported resolved Override Type Code.")
        return
    errors = []
    if type_code == "INSUFFICIENT_FUNDS" and (amount is None or amount <= 0):
        errors.append("Insufficient Funds requires a finite amount greater than zero, including when disabled.")
    if type_code == "CLOSED_PERIOD" and _supplied(raw):
        errors.append("Closed Period must not supply an override amount.")
    amount_id = checks.add("amount", "rule_header", "amount", "Override amount", errors,
                           prerequisites=[type_id], supplied=raw)
    if type_code != "INSUFFICIENT_FUNDS":
        return
    prerequisites = [type_id, amount_id, max_id, enabled_id]
    if not all(checks.passed(identifier) for identifier in prerequisites):
        checks.add("maximum.coverage", "rule_header", "controlBudget.maximumOverrideAmount",
                   "Enabled Insufficient Funds maximum coverage", prerequisites=prerequisites,
                   reason="Maximum coverage requires valid type, rule amount, header maximum and enabled flag.")
    elif rule.get("enabledFlag", "Y") == "Y":
        errors = []
        if maximum is None or maximum <= 0:
            errors.append("An enabled Insufficient Funds rule requires a positive parent MaximumOverrideAmount.")
        elif java_int_value(amount) > java_int_value(maximum):
            errors.append("Override amount exceeds the parent maximum using source-compatible Java intValue comparison.")
        evidence = {"comparison": "Java BigDecimal.intValue (truncate then signed 32-bit wrap)",
                    "ruleIntValue": java_int_value(amount),
                    "maximumIntValue": java_int_value(maximum) if maximum is not None else None}
        checks.add("maximum.coverage", "rule_header", "controlBudget.maximumOverrideAmount",
                   "Enabled Insufficient Funds maximum coverage", errors, prerequisites=prerequisites,
                   supplied=max_raw, evidence=evidence)
    else:
        checks.add("maximum.coverage", "rule_header", "controlBudget.maximumOverrideAmount",
                   "Enabled Insufficient Funds maximum coverage", prerequisites=prerequisites,
                   evidence={"applicable": False, "reason": "Rule is explicitly disabled."})


def prepare_override_rules(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Collect every independent local finding and withhold all rows on any failure."""
    if not isinstance(payload, Mapping):
        raise OverrideInputError("Input must be an object.")
    budget = payload.get("controlBudget")
    budget = budget if isinstance(budget, dict) else {}
    raw_rules = payload.get("overrideRules")
    if not isinstance(raw_rules, list):
        raise OverrideInputError("overrideRules must be an array.")
    counts = Counter(rule.get("ruleName") for rule in raw_rules
                     if isinstance(rule, dict) and _text(rule.get("ruleName")))
    prepared = []
    rows: dict[str, list[dict[str, str]]] = {name: [] for name in HEADERS}
    for index, raw in enumerate(raw_rules):
        rule = raw if isinstance(raw, dict) else {}
        name = rule.get("ruleName") if _text(rule.get("ruleName")) else f"<rule {index + 1}>"
        checks = _Checks(name, f"overrideRules.{index}")
        checks.add("parent", "rule_header", "controlBudget.name", "Parent Control Budget identity",
                   [] if _text(budget.get("name")) else ["Resolved parent Control Budget Name is required."])
        eligibility = []
        if budget.get("fvTypeCode") != "ORA_CONSUMPTION":
            eligibility.append("Override preparation currently supports only ORA_CONSUMPTION processing type.")
        if budget.get("allowOverridesFlag") != "Y":
            eligibility.append("Parent AllowOverridesFlag must be explicitly Y; it is never enabled automatically.")
        checks.add("eligibility", "rule_header", "controlBudget.fvTypeCode", "Override Rule eligibility", eligibility)
        checks.add("name", "rule_header", "ruleName", "Override Rule Name",
                   [] if _text(rule.get("ruleName")) and len(rule["ruleName"]) <= 100 else
                   ["Override Rule Name must be nonblank text of at most 100 characters."], supplied=rule.get("ruleName"))
        checks.add("identity", "rule_header", "ruleName", "Override Rule identity uniqueness",
                   ["Duplicate Override Rule Name within the parent budget."] if counts.get(name, 0) > 1 else [])
        description = rule.get("description", "")
        checks.add("description", "rule_header", "description", "Override Rule Description",
                   [] if isinstance(description, str) and len(description) <= 240 else
                   ["Description must be text of at most 240 characters when supplied."], supplied=description)
        enabled = rule.get("enabledFlag", "Y")
        enabled_id = checks.add("enabled", "rule_header", "enabledFlag", "Override Rule EnabledFlag",
                                [] if enabled in ("Y", "N") else ["EnabledFlag must be Y or N."], supplied=enabled)
        override_type = rule.get("overrideType")
        code = override_type.get("lookupCode") if isinstance(override_type, dict) else None
        type_id = checks.add("type", "rule_header", "overrideType.lookupCode", "Override Type Code",
                             [] if isinstance(code, str) and code in OVERRIDE_TYPES else
                             ["Supply a current-target LookupCode from XCC_CB_OVERRIDE_TYPE_CODE: INSUFFICIENT_FUNDS or CLOSED_PERIOD."],
                             supplied=code)
        _amounts(rule, budget, code, type_id, enabled_id, checks)
        codes, all_types = _transaction_types(rule, checks)
        all_sources, all_categories, journals = _journals(rule, codes, all_types, checks)
        users = _users(rule, checks)
        prepared.append({"ruleName": name, "status": "blocked" if checks.blocked else "ready", "checks": checks.items})
        if not checks.blocked:
            def row(member: str, values: list[str]) -> None:
                rows[member].append(dict(zip(HEADERS[member], values)))
            parent = budget["name"]
            row(RULE_CSV, [parent, name, description, code, str(rule["amount"]) if _supplied(rule.get("amount")) else "",
                           enabled, all_types, all_sources, all_categories])
            if all_types == "N":
                for transaction in codes:
                    row(TRANSACTION_CSV, [parent, name, transaction])
            for source, category in journals:
                row(JOURNAL_CSV, [parent, name, source, category])
            for user in users:
                row(APPROVER_CSV, [parent, name, user])
    blocked = any(rule["status"] == "blocked" for rule in prepared)
    warnings = []
    if not raw_rules and budget.get("allowOverridesFlag") == "Y":
        warnings.append({"check": "Override rules not supplied", "message": "AllowOverridesFlag is Y without Override Rules; this is a warning only."})
    return {"controlBudget": budget.get("name", ""), "status": "blocked" if blocked else "ready",
            "packageReady": not blocked, "overrideRules": prepared,
            "csvRows": {name: [] for name in HEADERS} if blocked else rows, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, type=Path, help="Normalized resolved JSON input")
    parser.add_argument("--output", type=Path, help="New preparation JSON result; refuses overwrite")
    parser.add_argument("--dry-run", action="store_true", help="Print validation and row preview without writing a file")
    args = parser.parse_args(argv)
    if not args.dry_run and args.output is None:
        parser.error("--output is required unless --dry-run is selected")
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8-sig"), parse_float=_JsonDecimalToken)
        result = prepare_override_rules(payload)
        rendered = json.dumps(result, indent=2, ensure_ascii=False, default=_json_default) + "\n"
        if args.dry_run:
            print(rendered, end="")
        else:
            with args.output.open("x", encoding="utf-8") as output:
                output.write(rendered)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Override preparation failed: {exc}\n")
    return 0 if result["packageReady"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
