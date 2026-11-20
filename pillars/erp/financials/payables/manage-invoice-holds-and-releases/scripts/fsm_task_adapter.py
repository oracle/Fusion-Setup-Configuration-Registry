#!/usr/bin/env python3
"""Invoice Holds domain rules over the Payables offline FSM package runtime."""

from __future__ import annotations

import importlib.util as _import_util
from pathlib import Path as _Path
import sys as _sys

_TASK_ROOT = _Path(__file__).resolve().parents[1]
_PACKAGE_RUNTIME = _TASK_ROOT / "scripts/fsm_package_runtime.py"
_RUNTIME_MODULE_NAME = "_payables_invoice_holds_package_runtime_v1"
_runtime = _sys.modules.get(_RUNTIME_MODULE_NAME)
if _runtime is None:
    _spec = _import_util.spec_from_file_location(_RUNTIME_MODULE_NAME, _PACKAGE_RUNTIME)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Cannot load the local FSM package runtime: {_PACKAGE_RUNTIME}")
    _runtime = _import_util.module_from_spec(_spec)
    _sys.modules[_RUNTIME_MODULE_NAME] = _runtime
    _spec.loader.exec_module(_runtime)
_runtime.bind_runtime(globals(), contract_path=_TASK_ROOT / "e2e-adapter.json")

# Task-owned scalar, date, lifecycle, and create rules extend the local runtime.

# Preserve these scalar/date/lifecycle/create extensions when regenerating the
# generic base. Task-specific behavior and tests are maintained together here.
# Source-conditional contract; no deployed-version or persisted-state claim.
_holds_generic_validate_field_value = _validate_field_value
_holds_generic_normalize_field_value = _normalize_field_value
_holds_generic_normalized_blueprint = _normalized_blueprint
_holds_generic_validate_blueprint = _validate_blueprint
_holds_generic_csv_bytes = _csv_bytes
_holds_generic_validate_candidate = validate_candidate
_holds_generic_read_package = _read_package

_HOLDS_OPTIONAL_CLEAR_FIELDS = frozenset({
    "ExternalDescription", "HoldInstruction", "WaitBeforeNotifyDays", "ReminderDays", "InitiateWorkflowFlag",
})
_HOLDS_TEXT_PRECISION = {"HoldLookupCode": 25, "HoldType": 25,
                         "ExternalDescription": 80, "HoldInstruction": 2000}
_HOLDS_LONG_FIELDS = frozenset({"WaitBeforeNotifyDays", "ReminderDays"})
_HOLDS_LITERAL_FLAGS = frozenset({"UserUpdateableFlag", "UserReleaseableFlag", "InitiateWorkflowFlag"})
_HOLDS_LONG_MAX = (1 << 63) - 1  # java.lang.Long representability, not business maximum.
_HOLDS_CSV_CELL_UTF8_MAX = 4000  # Maximum UTF-8 bytes per CSV cell.
# Required materialized row, including the two omission-only create defaults.
_HOLDS_CREATE_REQUIRED_FIELDS = ("HoldLookupCode", "HoldType", "DspDescription",
                                 "UserUpdateableFlag", "UserReleaseableFlag", "PostableFlag")
_HOLDS_CREATE_DEFAULTS = {
    "UserUpdateableFlag": {"value": "Y", "sourceIds": ["HOLDS-DEFAULTS"]},
    "PostableFlag": {"value": "N", "sourceIds": ["HOLDS-DEFAULTS"]},
}


def _holds_utf8_size(value, field):
    qualified = f"AP_HOLD_CODE.{field}"
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise AdapterError(f"{qualified} is not valid UTF-8 text.") from exc
    if size > _HOLDS_CSV_CELL_UTF8_MAX:
        raise AdapterError(
            f"{qualified} exceeds the FSM CSV staging limit of 4000 UTF-8 bytes; received {size}."
        )
    return size


def _holds_long(value, field):
    qualified = f"AP_HOLD_CODE.{field}"
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise AdapterError(f"{qualified} expects a source-compatible nonnegative java.lang.Long decimal integer.")
    if isinstance(value, str):
        if re.fullmatch(r"[+-]?[0-9]+", value) is None:
            raise AdapterError(f"{qualified} expects a source-compatible ASCII decimal integer without whitespace.")
        # Bound digit count before int conversion, including hostile huge strings.
        digits = value.lstrip("+-").lstrip("0") or "0"
        if len(digits) > 19:
            raise AdapterError(f"{qualified} exceeds java.lang.Long representability.")
        number = int(("-" if value.startswith("-") else "") + digits)
    else:
        number = value
    if number < 0 or number > _HOLDS_LONG_MAX:
        raise AdapterError(f"{qualified} must be >= 0 and representable by java.lang.Long.")
    return number


def _validate_field_value(entity, field, value, operation_id):
    if entity.get("name") != "AP_HOLD_CODE":
        return _holds_generic_validate_field_value(entity, field, value, operation_id)
    if field in _HOLDS_OPTIONAL_CLEAR_FIELDS and value == "":
        return
    if field in _HOLDS_LITERAL_FLAGS:
        if not isinstance(value, str) or value not in {"Y", "N"}:
            raise AdapterError(f"{entity['name']}.{field} expects a source-compatible literal string Y or N.")
        return
    if field in _HOLDS_LONG_FIELDS:
        _holds_long(value, field)
        return
    if field in _HOLDS_TEXT_PRECISION:
        if not isinstance(value, str):
            raise AdapterError(f"{entity['name']}.{field} expects a source-compatible string; normalize explicit null to a clear first.")
        _holds_utf8_size(value, field)
        # Java String.length counts UTF-16 code units, including surrogate pairs.
        actual = len(value.encode("utf-16-le")) // 2
        maximum = _HOLDS_TEXT_PRECISION[field]
        if actual > maximum:
            raise AdapterError(f"{entity['name']}.{field} exceeds {maximum} UTF-16 code units; received {actual}.")
        return
    if field == "DspDescription":
        if not isinstance(value, str):
            raise AdapterError("AP_HOLD_CODE.DspDescription expects a source-compatible string.")
        if not value.strip():
            raise AdapterError("AP_HOLD_CODE.DspDescription requires a nonblank description string.")
        _holds_utf8_size(value, field)
        return
    return _holds_generic_validate_field_value(entity, field, value, operation_id)


def _normalize_field_value(entity, field, value, operation_id):
    if entity.get("name") == "AP_HOLD_CODE":
        if field in _HOLDS_OPTIONAL_CLEAR_FIELDS and (value is None or value == ""):
            return ""
        if field in _HOLDS_LITERAL_FLAGS:
            _validate_field_value(entity, field, value, operation_id)
            return value
        if field in _HOLDS_LONG_FIELDS:
            return str(_holds_long(value, field))
        if field in _HOLDS_TEXT_PRECISION:
            return value  # No stripping, case folding, truncation, or Unicode normalization.
    return _holds_generic_normalize_field_value(entity, field, value, operation_id)


def _holds_clear_notice(operation):
    clears = sorted(field for field, value in operation.get("values", {}).items()
                    if field in _HOLDS_OPTIONAL_CLEAR_FIELDS and value == "")
    if operation.get("entity") != "AP_HOLD_CODE" or operation.get("action") != "update" or not clears:
        return None
    return {
        "code": "EXPLICIT_OPTIONAL_CLEAR", "operationId": operation["id"],
        "entity": operation["entity"], "fields": clears,
        "message": "Explicit null or empty input becomes a CSV empty cell and source-defined XML null. Omitted fields preserve baseline values.",
    }


def _normalized_blueprint(contract, design):
    blueprint = _holds_generic_normalized_blueprint(contract, design)
    for operation in blueprint["operations"]:
        notice = _holds_clear_notice(operation)
        if notice is not None and notice not in blueprint["warnings"]:
            blueprint["warnings"].append(notice)
    return blueprint


def validate_candidate(contract, template_path, baseline_path, blueprint_path,
                       requirements_path, candidate_path):
    result = _holds_generic_validate_candidate(
        contract, template_path, baseline_path, blueprint_path, requirements_path, candidate_path)
    blueprint = _read_json(blueprint_path)
    # The unchanged validator has already checked identity, operation, fields,
    # values, baseline, candidate and requirements. Match the complete known
    # disclosure to those actual clears; a code string alone never resolves a
    # warning. Preserve visible warnings and every unknown/uncertainty blocker.
    notices = [notice for operation in blueprint["operations"]
               if (notice := _holds_clear_notice(operation)) is not None]
    result["unresolvedWarnings"] = [warning for warning in result["unresolvedWarnings"]
                                    if warning not in notices]
    return result


def _read_package(path, contract):
    if path.suffix.lower() != ".zip":
        raise AdapterError(f"FSM package must use a .zip file: {path}.")
    package = _holds_generic_read_package(path, contract)
    # Exact source-package qualification for this task. Other completion labels
    # may exist in Oracle; they require evidence before this adapter admits them.
    if (contract['task']['code'] == 'AP_MANAGE_INVOICE_HOLDS_AND_RELEASES'
            and package.metadata['ProcessStatus'] != 'COMPLETED'):
        raise AdapterError(
            'evidence_unresolved: Invoice Holds source package ProcessStatus must be the evidenced exact COMPLETED value; received '
            + repr(package.metadata['ProcessStatus'])
            + '. Obtain a qualified completed export or review this status before reuse.'
        )
    return package


def _csv_bytes(headers, rows):
    for row in rows:
        for field in headers:
            value = row.get(field, "")
            _holds_utf8_size("" if value is None else str(value), field)
    return _holds_generic_csv_bytes(headers, rows)


def _validate_blueprint(contract, blueprint, baseline=None):
    _holds_generic_validate_blueprint(contract, blueprint, baseline)
    for operation in blueprint["operations"]:
        for flag in ("preserveOtherValues", "preserveUnspecifiedRows"):
            if operation.get(flag, True) is not True:
                raise AdapterError("Invoice Holds bounded profile requires full value and row preservation; " + flag + " must be true.")
        entity = _entity_map(contract)[operation["entity"]]
        # Canonical normalized blueprints contain the actual CSV clear value.
        if any(value is None for value in operation["values"].values()):
            raise AdapterError("Normalize explicit null before using a canonical blueprint.")
        if operation["action"] == "create":
            final = {header: "" for header in entity["headers"]}
            final.update(operation["targetKey"])
            final.update(operation["values"])
            required = tuple(dict.fromkeys(_HOLDS_CREATE_REQUIRED_FIELDS
                + tuple(entity.get("createRequiredFields", []))))
            missing = [field for field in required if not str(final.get(field, "")).strip()]
            if missing:
                raise AdapterError("AP_HOLD_CODE create requires explicit nonblank fields: " + ", ".join(missing) + ".")
            if final["HoldLookupCode"].upper().startswith("ORA_"):
                raise AdapterError("AP_HOLD_CODE.HoldLookupCode ORA_ prefix is reserved; choose a user-defined create key.")
            for field in ("HoldLookupCode", "HoldType", "DspDescription", "UserReleaseableFlag",
                          "UserUpdateableFlag", "PostableFlag"):
                _validate_field_value(entity, field, final[field], operation["id"])
            materialized, _ = _holds_create_materialization(operation["values"], operation=operation)
            final.update(materialized)
        else:
            if baseline is None:
                continue  # Intent-only checks cannot claim baseline-dependent routing readiness.
            row = _row_index(baseline, entity)[_target_tuple(entity, operation["targetKey"])]
            final = {**row, **operation["values"]}
            required_values = {**row, "DspDescription": final.get("DspDescription", "")}
            missing = [field for field in entity["requiredFields"]
                       if not str(required_values.get(field, "")).strip()]
            if missing:
                raise AdapterError("Invoice Holds bounded profile requires nonblank required fields: " + ", ".join(missing) + ".")
            # Unrequested blank baseline flags remain blank. Possible importer
            # defaults are verified after import, not a pre-import proof gate.
            for field in ("UserReleaseableFlag", "UserUpdateableFlag", "PostableFlag"):
                if field == "PostableFlag" and row.get(field) == "X":
                    # Preserve source data; explicit requested values are validated separately.
                    continue
                if row.get(field, "") != "":
                    _validate_field_value(entity, field, row[field], operation["id"])
        for field in _HOLDS_OPTIONAL_CLEAR_FIELDS:
            _validate_field_value(entity, field, final.get(field, ""), operation["id"])
        workflow = final.get("InitiateWorkflowFlag", "")
        if workflow != "":
            _validate_field_value(entity, "InitiateWorkflowFlag", workflow, operation["id"])
        # EO condition is exact HoldLookupCode, not HoldType or a case-folded key.
        if (final.get("UserReleaseableFlag") == "N" and workflow == "Y"
                and final.get("HoldLookupCode") != "INCOMPLETE INVOICE"):
            raise AdapterError("AP_HOLD_RES_ROUTING_NO: workflow Y with manual release N requires exact hold code INCOMPLETE INVOICE.")
        for field, value in final.items():
            if field not in entity["auditFields"]:
                _holds_utf8_size(str(value), field)


# InactiveDate serialization extends scalar validation before lifecycle rules.
# No Oracle source execution or deployed behavior is claimed by local tests.
_holds_date_prior_read_package = _read_package
_holds_date_prior_csv_bytes = _csv_bytes
_holds_date_prior_validate_field = _validate_field_value
_holds_date_prior_normalize_field = _normalize_field_value
_holds_date_prior_semantic_issues = _semantic_issues
_holds_date_prior_reconcile = reconcile

_HOLDS_DATE_FIELD = "InactiveDate"
_HOLDS_DATE_SOURCE_IDS = ["HOLDS-FIELD-CONTRACT", "HOLDS-IMPORT-EFFECTS", "HOLDS-SERIALIZATION", "HOLDS-CALENDAR-CONTRACT"]
_HOLDS_OPTIONAL_CLEAR_FIELDS = set(_HOLDS_OPTIONAL_CLEAR_FIELDS) | {_HOLDS_DATE_FIELD}


def _holds_date_canonical(value, *, source=False):
    """A calendar representation; never trim, infer, or truncate."""
    if value is None and not source:
        return ""
    if value == "":
        return ""
    if not isinstance(value, str):
        raise AdapterError("AP_HOLD_CODE.InactiveDate expects a source-compatible explicit YYYY-MM-DD calendar date or null/empty clear.")
    groups = None
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        groups = value.split("-")
    elif source and re.fullmatch(r"[0-9]{4}/[0-9]{2}/[0-9]{2}", value):
        groups = value.split("/")
    elif source and re.fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", value):
        month, day, year = value.split("/")
        groups = (year, month, day)
    if groups is None:
        classification = "evidence_unresolved: source representation for " if source else ""
        raise AdapterError(classification + "AP_HOLD_CODE.InactiveDate expects a source-compatible date-only representation; no whitespace, relative date, timestamp or timezone is inferred.")
    try:
        parsed = date(*map(int, groups))
    except ValueError as exc:
        raise AdapterError("AP_HOLD_CODE.InactiveDate is not a real Gregorian calendar date.") from exc
    return parsed.isoformat()


def _validate_field_value(entity, field, value, operation_id):
    if entity.get("name") == "AP_HOLD_CODE" and field == _HOLDS_DATE_FIELD:
        if value is None:
            raise AdapterError("Normalize AP_HOLD_CODE.InactiveDate explicit null to an empty clear before validating a canonical blueprint.")
        _holds_date_canonical(value)
        return
    return _holds_date_prior_validate_field(entity, field, value, operation_id)


def _normalize_field_value(entity, field, value, operation_id):
    if entity.get("name") == "AP_HOLD_CODE" and field == _HOLDS_DATE_FIELD:
        return _holds_date_canonical(value)
    return _holds_date_prior_normalize_field(entity, field, value, operation_id)


def _read_package(path, contract):
    package = _holds_date_prior_read_package(path, contract)
    package._holds_date_raw_rows = {}
    for entity in contract["package"]["entities"]:
        if entity["name"] != "AP_HOLD_CODE" or _HOLDS_DATE_FIELD not in entity["headers"]:
            continue
        raw = package._holds_date_raw_rows.setdefault(entity["name"], {})
        for row in package.rows[entity["name"]]:
            key = _row_key(entity, row)
            raw[key] = row[_HOLDS_DATE_FIELD]
            row[_HOLDS_DATE_FIELD] = _holds_date_canonical(row[_HOLDS_DATE_FIELD], source=True)
    # member_bytes and archive_sha256 remain the exact original evidence.
    return package


def _csv_bytes(headers, rows):
    if _HOLDS_DATE_FIELD not in headers:
        return _holds_date_prior_csv_bytes(headers, rows)
    output = []
    for row in rows:
        rendered = dict(row)
        value = _holds_date_canonical(rendered.get(_HOLDS_DATE_FIELD, ""), source=True)
        rendered[_HOLDS_DATE_FIELD] = value.replace("-", "/") if value else ""
        output.append(rendered)
    return _holds_date_prior_csv_bytes(headers, output)


def _semantic_issues(contract, candidate, baseline, blueprint, requirements):
    issues = _holds_date_prior_semantic_issues(contract, candidate, baseline, blueprint, requirements)
    entities = _entity_map(contract)
    for operation in blueprint["operations"]:
        if operation["action"] != "create":
            continue
        entity = entities[operation["entity"]]
        row = _row_index(candidate, entity).get(_target_tuple(entity, operation["targetKey"]))
        if row is None:
            continue  # The generic validator reports the missing target.
        expected = {header: "" for header in entity["headers"]}
        expected.update(operation["targetKey"])
        expected.update(operation["values"])
        for field in entity["headers"]:
            if field not in entity["auditFields"] and row[field] != str(expected[field]):
                issues.append({"code": "UNEXPECTED_CREATE_VALUE",
                    "message": entity["name"] + " create field " + field
                    + " differs from the complete requested/source-effect row, including omitted optional blanks."})
    for entity in contract["package"]["entities"]:
        if entity["name"] != "AP_HOLD_CODE":
            continue
        raw = getattr(candidate, "_holds_date_raw_rows", {}).get(entity["name"], {})
        for row in candidate.rows[entity["name"]]:
            key = _row_key(entity, row)
            expected = row[_HOLDS_DATE_FIELD].replace("-", "/")
            if key not in raw or raw[key] != expected:
                issues.append({"code": "DATE_WIRE_FORMAT",
                    "message": "AP_HOLD_CODE " + repr(key) + " InactiveDate must use uniform YYYY/MM/DD date-only CSV or exact empty; mixed cached input formats are unsafe."})
    return issues


def _holds_date_normalization_evidence(contract, packages):
    evidence = []
    for label, package in packages.items():
        for entity in contract["package"]["entities"]:
            if entity["name"] != "AP_HOLD_CODE":
                continue
            raw = getattr(package, "_holds_date_raw_rows", {}).get(entity["name"], {})
            for row in sorted(package.rows[entity["name"]], key=lambda item: _row_key(entity, item)):
                key = _row_key(entity, row)
                if raw.get(key) != row[_HOLDS_DATE_FIELD]:
                    evidence.append({"packageRole": label, "packageSha256": package.archive_sha256,
                        "entity": entity["name"], "targetKey": dict(zip(entity["keyFields"], key)),
                        "field": _HOLDS_DATE_FIELD, "rawValue": raw.get(key),
                        "canonicalValue": row[_HOLDS_DATE_FIELD],
                        "ruleId": "HOLDS-DATE-CALENDAR-EQUIVALENCE",
                        "sourceIds": list(_HOLDS_DATE_SOURCE_IDS)})
    return evidence


def _holds_date_serialization_evidence(contract, baseline, blueprint):
    """Reviewable representation changes, derived from exact baseline and intent."""
    entities = _entity_map(contract)
    payload_rows = []
    for operation in blueprint["operations"]:
        if operation["entity"] != "AP_HOLD_CODE":
            continue
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        before = _row_index(baseline, entity).get(key)
        if before is None and operation["action"] != "create":
            raise AdapterError("Date serialization evidence requires an exact existing AP_HOLD_CODE target.")
        raw = None if before is None else baseline._holds_date_raw_rows[entity["name"]][key]
        original = None if before is None else before[_HOLDS_DATE_FIELD]
        canonical = operation["values"].get(_HOLDS_DATE_FIELD, "" if before is None else original)
        requested = operation.get("requestedValues", operation["values"])
        payload_rows.append({"operationId": operation["id"], "entity": entity["name"],
            "targetKey": dict(zip(entity["keyFields"], key)), "field": _HOLDS_DATE_FIELD,
            "baselineRawValue": raw, "baselineCanonicalValue": original,
            "payloadCanonicalValue": canonical, "payloadCsvValue": canonical.replace("-", "/"),
            "explicitlyRequested": _HOLDS_DATE_FIELD in requested,
            "calendarValueChanged": None if before is None else canonical != original,
            "lexicalValueChanged": None if before is None else raw != canonical.replace("-", "/")})
    return {"ruleId": "HOLDS-DATE-UNIFORM-COLUMN-SERIALIZATION",
        "baselineSha256": baseline.archive_sha256,
        "canonicalFormat": "YYYY-MM-DD", "payloadCsvFormat": "YYYY/MM/DD", "emptyValue": "",
        "scope": "Every nonblank InactiveDate cell in serialized target rows uses one date-only format, including dates not requested for change. Untargeted rows are not serialized.",
        "preservation": "Calendar-value equality; original lexical values remain evidence and are not promised as output formatting.",
        "baselineNormalization": _holds_date_normalization_evidence(contract, {"baseline": baseline}),
        "payloadRows": payload_rows, "sourceIds": list(_HOLDS_DATE_SOURCE_IDS)}


def reconcile(contract, baseline_path, candidate_path, blueprint_path, requirements_path, export_path):
    result = _holds_date_prior_reconcile(contract, baseline_path, candidate_path,
        blueprint_path, requirements_path, export_path)
    packages = {"baseline": _read_package(baseline_path, contract),
                "candidate": _read_package(candidate_path, contract),
                "persisted": _read_package(export_path, contract)}
    result["dateNormalizationEvidence"] = _holds_date_normalization_evidence(contract, packages)
    return result


# Task-owned manual-release and accounting rules; no external calls.
from copy import deepcopy as _holds_copy

_holds_scalar_normalized = _normalized_blueprint
_holds_scalar_validate_blueprint = _validate_blueprint
_holds_scalar_requirements = _requirements
_holds_scalar_reconcile = reconcile
_holds_scalar_rollback = make_rollback
_holds_scalar_clear_notice = _holds_clear_notice
_holds_scalar_candidate_validate = validate_candidate

_HOLDS_MANUAL = "UserReleaseableFlag"
_HOLDS_ROUTING_DETAILS = {"WaitBeforeNotifyDays": "", "ReminderDays": "", "HoldInstruction": ""}
_HOLDS_MANUAL_EFFECTS = {"InitiateWorkflowFlag": "N", "WaitBeforeNotifyDays": "",
                         "ReminderDays": "", "HoldInstruction": ""}
_HOLDS_MANUAL_SOURCE_IDS = ["HOLDS-IMPORT-EFFECTS", "HOLDS-FIELD-CONTRACT", "HOLDS-IMPORT-CONTRACT"]
_HOLDS_DERIVED_KEYS = {"requestedValues", "sourceDrivenEffects", "potentialSourceDrivenEffects", "baselineValueSha256", "accountingEffects"}
_HOLDS_ACCOUNTING = "PostableFlag"
_HOLDS_ACCOUNTING_SOURCE_IDS = ["HOLDS-IMPORT-EFFECTS", "HOLDS-ACCOUNTING-EFFECTS"]
_HOLDS_RELEASE_TYPES_WITH_KNOWN_EFFECTS = frozenset({
    "HOLD QUICK RELEASE REASON", "INV QUICK RELEASE REASON", "INVOICE RELEASE REASON",
    "MATCHING RELEASE REASON", "VARIANCE RELEASE REASON",
})  # Five-type create consistency rule; other HoldType codes remain accepted.
_HOLDS_MANUAL_UPDATE_RESTRICTED_TYPES = frozenset({
    "HOLD QUICK RELEASE REASON", "INV QUICK RELEASE REASON", "INVOICE RELEASE REASON",
    "MATCHING RELEASE REASON", "VARIANCE RELEASE REASON",
})


def _holds_validate_update_restrictions(contract, blueprint, baseline):
    """Enforce task update eligibility using the existing row and explicit intent."""
    if baseline is None:
        return  # Intent-only validation cannot establish baseline eligibility.
    entities = _entity_map(contract)
    for operation in blueprint.get("operations", []):
        if operation.get("action") != "update":
            continue
        entity = entities.get(operation.get("entity"))
        target = operation.get("targetKey")
        if entity is None or not isinstance(target, dict) or any(
                field not in target for field in entity["keyFields"]):
            continue  # The structural validator reports malformed intent.
        before = _row_index(baseline, entity).get(_target_tuple(entity, target))
        if before is None:
            continue  # The structural validator requires exactly one target.
        # requestedValues has already been independently checked against the
        # materialized values. Omitted setter effects are not explicit requests.
        requested = operation.get("requestedValues", operation.get("values", {}))
        if not isinstance(requested, dict):
            continue
        context = (f"Operation {operation.get('id')}, {entity['name']} key {target!r}; "
                   f"baseline HoldType={before.get('HoldType')!r}, "
                   f"UserUpdateableFlag={before.get('UserUpdateableFlag')!r}, "
                   f"UserReleaseableFlag={before.get(_HOLDS_MANUAL)!r}, "
                   f"InitiateWorkflowFlag={before.get('InitiateWorkflowFlag')!r}")
        for field in ("InactiveDate", "DspDescription"):
            if (field in requested and requested[field] != before[field]
                    and before.get("UserUpdateableFlag") == "N"):
                raise AdapterError("UPDATE_FIELD_REQUIRES_UPDATEABLE: " + context
                    + f"; field {field}: a change is prohibited when baseline UserUpdateableFlag=N.")
        # Accounting and manual release share the approved task policy. These
        # task conditions are enforced by the adapter; they do not claim the
        # importer independently enforces them.
        for field in (_HOLDS_MANUAL, _HOLDS_ACCOUNTING):
            if field not in requested or requested[field] == before[field]:
                continue
            if before.get("HoldType") in _HOLDS_MANUAL_UPDATE_RESTRICTED_TYPES:
                raise AdapterError("UPDATE_TYPE_RESTRICTED_FIELD: " + context
                    + f"; field {field}: changes are prohibited for this type.")
            if before.get("UserUpdateableFlag") != "Y":
                raise AdapterError("UPDATE_FIELD_REQUIRES_UPDATEABLE: " + context
                    + f"; field {field}: a change requires baseline UserUpdateableFlag=Y.")
        routing = "InitiateWorkflowFlag"
        if (routing in requested and requested[routing] != before[routing]
                and (before.get(_HOLDS_MANUAL) == "N" or before.get("UserUpdateableFlag") == "N")):
            raise AdapterError("UPDATE_ROUTING_RESTRICTED: " + context
                + f"; field {routing}: a change is prohibited when either baseline flag is N.")
        # An eligible routing change applies to detail validation in this same
        # request. A retained blank or requested clear must not be treated as Y;
        # use the N eligibility branch without rewriting the preserved CSV cell.
        baseline_routing = "N" if before.get(routing) == "" else before.get(routing)
        effective_routing = requested.get(routing, baseline_routing)
        if effective_routing == "":
            effective_routing = "N"  # Neither retained blanks nor requested clears enable routing.
        for field in ("WaitBeforeNotifyDays", "ReminderDays", "HoldInstruction"):
            # Explicit empty values agree with routing-off cleanup. Baseline
            # updateability still governs explicit detail changes.
            routing_off_clear = (requested.get(routing, before.get(routing)) == "N"
                                 and requested.get(field) == "")
            if (field in requested and requested[field] != before[field]
                    and ((effective_routing == "N" and not routing_off_clear)
                         or before.get("UserUpdateableFlag") == "N")):
                raise AdapterError("UPDATE_ROUTING_DETAIL_RESTRICTED: " + context
                    + f"; effective InitiateWorkflowFlag={effective_routing!r}; field {field}: "
                      "a change is prohibited when routing is N or baseline UserUpdateableFlag=N.")


def _holds_validate_import_consistency(requested, *, create=False, before=None, operation=None):
    """Reject supplied values that conflict with an active deterministic setter."""
    operation = operation or {}
    context = (f"Operation {operation.get('id', '<intent>')}, AP_HOLD_CODE "
               f"key {operation.get('targetKey', {})!r}")
    if before is not None:
        context += f"; baseline UserReleaseableFlag={before.get(_HOLDS_MANUAL)!r}"
    if create and requested.get("HoldType") in _HOLDS_RELEASE_TYPES_WITH_KNOWN_EFFECTS:
        for field in (_HOLDS_MANUAL, _HOLDS_ACCOUNTING):
            if requested.get(field) == "Y":
                required = "N" if field == _HOLDS_MANUAL else "N; omission defaults to N"
                raise AdapterError("RELEASE_TYPE_FLAG_CONFLICT: " + context
                    + f"; HoldType={requested['HoldType']!r}, field {field}: supplied Y; required {required} "
                    + "under the release-type create rule.")
    active = (requested.get(_HOLDS_MANUAL) == "N"
              and (create or (before is not None and before.get(_HOLDS_MANUAL) != "N")))
    for field, expected in (_HOLDS_MANUAL_EFFECTS.items() if active else ()):
        if field in requested and requested[field] != expected:
            raise AdapterError("MANUAL_RELEASE_DEPENDENCY_CONFLICT: " + context
                + f"; field {field}: supplied {requested[field]!r} conflicts with the required {expected!r} "
                + "for create or an actual transition to UserReleaseableFlag=N.")
    expected = dict(_HOLDS_MANUAL_EFFECTS) if active else {}
    routing = expected.get("InitiateWorkflowFlag",
        requested.get("InitiateWorkflowFlag", (before or {}).get("InitiateWorkflowFlag")))
    if routing == "N":
        for field in _HOLDS_ROUTING_DETAILS:
            if field in requested and requested[field] != "":
                raise AdapterError("ROUTING_DISABLED_DETAIL_CONFLICT: " + context
                    + f"; field {field}: supplied {requested[field]!r}; required blank when InitiateWorkflowFlag=N.")
        expected.update(_HOLDS_ROUTING_DETAILS)
    return expected


def _holds_create_materialization(requested, *, operation=None):
    """Validate supplied values and fill omitted deterministic setter outcomes."""
    expected = _holds_validate_import_consistency(requested, create=True, operation=operation)
    effects = {field: value for field, value in expected.items() if field not in requested}
    return {**requested, **effects}, effects


def _holds_potential_effects(requested, *, create=False):
    # Retain the established artifact field; accepted supplied values cannot
    # conflict with the deterministic effects checked during materialization.
    return {}


def _holds_setter_notice(operation, *, create=False, before=None):
    requested = operation.get("requestedValues", operation.get("values", {}))
    expected = _holds_validate_import_consistency(requested, create=create,
        before=before, operation=operation)
    if not expected:
        return None
    return {"code": "SOURCE_SETTER_EFFECTS_NOTICE", "blocking": False,
        "operationId": operation["id"], "entity": operation["entity"],
        "requiredValues": expected, "sourceIds": _holds_consistency_source_ids(operation),
        "message": "Pre-import consistency requires routing N and empty notification days, reminder days "
        "and instruction for create with manual release N or an actual transition to N. Conflicting "
        "supplied values are rejected; matching supplied values are preserved and omitted outcomes "
        "are materialized. The five named release types prohibit manual-release Y and accounting Y "
        "on create; accounting N and the omission default N remain valid. Independently, final "
        "routing N always requires empty instruction and notification/reminder days, including "
        "unchanged or omitted routing on an existing N row. This receipt "
        "records accepted input consistency, not a promised saved result. Fusion validates HoldType "
        "membership and effective dates during import without an environment type check."}


def _holds_consistency_source_ids(operation):
    requested = operation.get("requestedValues", operation.get("values", {}))
    if requested.get(_HOLDS_MANUAL) == "N":
        return list(_HOLDS_MANUAL_SOURCE_IDS) + ["HOLDS-ROUTING-OFF-CLEARS-DETAILS"]
    return ["HOLDS-ROUTING-OFF-CLEARS-DETAILS"]


def _holds_create_setter_notice(operation):
    if operation.get("action") != "create" or operation.get("entity") != "AP_HOLD_CODE":
        return None
    return _holds_setter_notice(operation, create=True)


def _holds_create_lookup_notice(operation):
    if operation.get("action") != "create" or operation.get("entity") != "AP_HOLD_CODE":
        return None
    return {"code": "SOURCE_LOOKUP_MAINTENANCE_NOTICE", "blocking": False,
        "operationId": operation["id"], "entity": operation["entity"],
        "lookupContext": {"lookupType": "HOLD CODE", "setId": 0, "viewApplicationId": 200,
                          "lookupCode": operation["targetKey"]["HoldLookupCode"]},
        "sourceIds": ["HOLDS-IMPORT-EFFECTS", "HOLDS-FIELD-CONTRACT"],
        "message": "Standard create maintenance deletes/reinserts the same-context supporting lookup "
        "when one already exists, using HoldLookupCode as meaning and the supplied DspDescription. "
        "This is a nonblocking source-effect disclosure, not a separate lookup-absence prerequisite "
        "or authorization for standalone lookup mutation. Fresh task data must establish that the "
        "AP_HOLD_CODE definition key is absent; its export does not prove independent shared-lookup absence. "
        "Retain actual import diagnostics; reconcile the exported description and other requested/defaulted "
        "values when requested or needed after failure, an uncertain outcome or before recovery, "
        "without claiming hidden-field or all-language preservation."}


def _holds_update_lookup_notice(operation, before):
    if operation.get("action") != "update" or operation.get("entity") != "AP_HOLD_CODE":
        return None
    final = {**before, **operation["values"]}
    description = final.get("DspDescription")
    if description is None:
        return None
    return {"code": "SOURCE_LOOKUP_MAINTENANCE_NOTICE", "blocking": False,
        "operationId": operation["id"], "entity": operation["entity"],
        "lookupContext": {"lookupType": "HOLD CODE", "setId": 0, "viewApplicationId": 200,
                          "lookupCode": operation["targetKey"]["HoldLookupCode"]},
        "descriptionAssignment": {"value": description,
            "role": "requested" if "DspDescription" in operation["values"] else "preserved",
            "changed": description != before.get("DspDescription")},
        "sourceIds": ["HOLDS-IMPORT-EFFECTS", "HOLDS-FIELD-CONTRACT"],
        "message": "Existing-row update with a nonnull description enters supporting lookup maintenance, "
        "including unchanged or preserved descriptions in a complete CSV row. It inserts an absent "
        "HOLD CODE/set0/application200 lookup or updates a present lookup using the supplied description "
        "and existing displayed meaning. SQL failures can be reported as FND_GENERIC_MESSAGE. "
        "This is a nonblocking source-effect disclosure; it requires no independent lookup receipt, "
        "saved-state proof or routine post-import verification. It does not authorize standalone "
        "lookup mutation or guarantee hidden-field, tag or all-language preservation or restoration. "
        "Retain actual import diagnostics; reconcile exported values when requested or needed after "
        "failure, an uncertain outcome or before recovery."}


def _holds_lookup_recovery_boundary(report):
    report["rollbackScope"] += (" This restores exported setup values only. Complete-row updates can "
        "run supporting lookup maintenance again; hidden lookup fields, tags and all language rows "
        "are not guaranteed to be preserved or restored.")
    report["lookupHiddenStateRestorationGuaranteed"] = False
    return report


def _holds_value_hash(entity, row):
    return _sha256_bytes(_canonical_bytes({field: row[field] for field in entity["headers"]
                                          if field not in entity["auditFields"]}))


def _holds_manual_materialization(entity, row, requested, *, operation=None):
    """Validate active setter consistency and derive only omitted outcomes."""
    expected = _holds_validate_import_consistency(requested, before=row, operation=operation)
    effects = {field: value for field, value in expected.items() if field not in requested}
    return {**requested, **effects}, effects


def _holds_accounting_effects(operation, before):
    """Disclose the update hook only for an actual requested accounting change."""
    if operation.get("action") != "update" or operation.get("entity") != "AP_HOLD_CODE":
        return {}
    requested = operation.get("requestedValues", operation.get("values", {}))
    if (_HOLDS_ACCOUNTING not in requested
            or requested[_HOLDS_ACCOUNTING] == before[_HOLDS_ACCOUNTING]):
        return {}
    return {"field": _HOLDS_ACCOUNTING, "beforeValue": before[_HOLDS_ACCOUNTING],
        "requestedValue": requested[_HOLDS_ACCOUNTING],
        "trigger": "DML_UPDATE with changed PostableFlag",
        "procedure": "update_postable_flag",
        "scope": "Matching invoices with unreleased holds; existing INCOMPLETE/UNPROCESSED "
        "invoice and related payment events when distribution event IDs exist.",
        "failureMessage": "FND_GENERIC_MESSAGE",
        "eventStateRestorationGuaranteed": False,
        "sourceIds": list(_HOLDS_ACCOUNTING_SOURCE_IDS)}


def _holds_accounting_notice(operation, before):
    effects = _holds_accounting_effects(operation, before)
    if not effects:
        return None
    return {"code": "SOURCE_ACCOUNTING_EFFECTS_NOTICE", "blocking": False,
        "operationId": operation["id"], "entity": operation["entity"],
        "accountingEffects": effects, "sourceIds": list(_HOLDS_ACCOUNTING_SOURCE_IDS),
        "message": "An actual PostableFlag update calls update_postable_flag for matching "
        "invoices with unreleased holds. It considers existing INCOMPLETE/UNPROCESSED invoice "
        "and related payment events when distribution event IDs exist; unreleased N or X "
        "holds can prevent event completion after distribution checks. Database errors are "
        "reported as FND_GENERIC_MESSAGE. This is a nonblocking source-effect disclosure, "
        "not proof of a saved flag or an event result. A reverse setup-flag update can run "
        "the hook again and does not guarantee restoration of prior accounting-event state. "
        "Ordinary Data Loader validation and approval remain required."}


def _holds_validate_accounting_effects(contract, blueprint, baseline):
    entities = _entity_map(contract)
    for operation in blueprint.get("operations", []):
        if operation.get("action") != "update":
            if "accountingEffects" in operation:
                raise AdapterError("Accounting-effect provenance applies only to an actual existing-row update.")
            continue
        if baseline is None:
            continue  # Intent-only checks cannot establish an actual change.
        entity = entities.get(operation.get("entity"))
        target = operation.get("targetKey")
        if entity is None or not isinstance(target, dict) or any(
                field not in target for field in entity["keyFields"]):
            continue  # The structural validator reports malformed intent.
        before = _row_index(baseline, entity).get(_target_tuple(entity, target))
        if before is None:
            continue
        expected = _holds_accounting_effects(operation, before)
        if operation.get("accountingEffects", {}) != expected:
            raise AdapterError("Accounting effects differ from independent baseline/request derivation.")
        notice = _holds_accounting_notice(operation, before)
        if notice is not None and notice not in blueprint.get("warnings", []):
            raise AdapterError("Accounting nonblocking source-effect disclosure is missing or differs from independent derivation.")


def _holds_clear_notice(operation):
    # A source-derived null is not an explicit user clear. Retain only actual
    # request disclosures; exact visible effects are separately in the preview.
    request = dict(operation)
    request["values"] = operation.get("requestedValues", operation.get("values", {}))
    return _holds_scalar_clear_notice(request)


def _normalized_blueprint(contract, design):
    if any(_HOLDS_DERIVED_KEYS.intersection(operation)
           for operation in design.get("operations", []) if isinstance(operation, dict)):
        raise AdapterError("Design must contain requested values only; source effects and baseline binding are derived.")
    if design.get("explicitDefaults"):
        raise AdapterError("Create default provenance is derived from omitted inputs; do not supply explicitDefaults.")
    entities = _entity_map(contract)
    for operation in design.get("operations", []):
        if isinstance(operation, dict) and operation.get("action") == "create":
            entity = entities.get(operation.get("entity"), {})
            if entity.get("name") == "AP_HOLD_CODE":
                _holds_validate_create_defaults(entity)
    result = _holds_scalar_normalized(contract, design)
    for operation in result["operations"]:
        if operation["action"] == "create" and operation["entity"] == "AP_HOLD_CODE":
            defaulted = {item["field"] for item in result["explicitDefaults"]
                         if item["operationId"] == operation["id"]}
            operation["requestedValues"] = {field: value for field, value in operation["values"].items()
                                            if field not in defaulted}
    return result


def _holds_validate_create_defaults(entity):
    if entity.get("createDefaults") != _HOLDS_CREATE_DEFAULTS:
        raise AdapterError("Invoice Holds create defaults must match the recorded UserUpdateableFlag=Y "
            "and PostableFlag=N metadata contract; no other create defaults are allowed.")


def _holds_defaulted_create_values(contract, operation, requested):
    """Reuse generic defaulting to independently derive values and receipts."""
    entity = _entity_map(contract)[operation["entity"]]
    _holds_validate_create_defaults(entity)
    intent = {key: operation[key] for key in ("id", "action", "entity", "targetKey")}
    intent["values"] = requested
    normalized = _holds_generic_normalized_blueprint(contract, {"operations": [intent]})
    return normalized["operations"][0]["values"], normalized["explicitDefaults"]


def _holds_bind_manual_effects(contract, blueprint, baseline):
    result = _holds_copy(blueprint)
    result.setdefault("warnings", [])
    entities = _entity_map(contract)
    # Validate intent shape and allowlist before indexing. This checks no
    # baseline-dependent routing until omitted dependent values are materialized.
    _holds_scalar_validate_blueprint(contract, result)
    _holds_generic_validate_blueprint(contract, result, baseline)
    _holds_validate_update_restrictions(contract, result, baseline)
    for operation in result["operations"]:
        if operation["action"] == "create":
            requested = dict(operation.get("requestedValues", operation["values"]))
            values, effects = _holds_create_materialization(operation["values"], operation=operation)
            operation.update(requestedValues=requested, sourceDrivenEffects=effects, values=values,
                             potentialSourceDrivenEffects=_holds_potential_effects(values, create=True))
            notice = _holds_create_setter_notice(operation)
            if notice is not None and notice not in result["warnings"]:
                result["warnings"].append(notice)
            notice = _holds_create_lookup_notice(operation)
            if notice is not None and notice not in result["warnings"]:
                result["warnings"].append(notice)
            continue
        if operation.get("entity") == "AP_HOLD_CODE" and operation.get("action") == "update":
            entity = entities[operation["entity"]]
            before = _row_index(baseline, entity).get(_target_tuple(entity, operation["targetKey"]))
            if before is not None:
                notice = _holds_update_lookup_notice(operation, before)
                if notice is not None and notice not in result["warnings"]:
                    result["warnings"].append(notice)
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        before = _row_index(baseline, entity).get(key)
        if before is None:
            raise AdapterError("Flag-update target must exist exactly once in the qualified baseline.")
        if (_HOLDS_MANUAL in operation["values"] or
                operation["values"].get("InitiateWorkflowFlag", before.get("InitiateWorkflowFlag")) == "N"):
            requested = dict(operation["values"])
            values, effects = _holds_manual_materialization(entity, before, requested, operation=operation)
            operation.update(requestedValues=requested, sourceDrivenEffects=effects,
                             potentialSourceDrivenEffects=_holds_potential_effects(requested),
                             baselineValueSha256=_holds_value_hash(entity, before), values=values)
            notice = _holds_setter_notice(operation, before=before)
            if notice is not None and notice not in result["warnings"]:
                result["warnings"].append(notice)
        effects = _holds_accounting_effects(operation, before)
        if effects:
            operation["accountingEffects"] = effects
        notice = _holds_accounting_notice(operation, before)
        if notice is not None and notice not in result["warnings"]:
            result["warnings"].append(notice)
    return result


def _validate_blueprint(contract, blueprint, baseline=None):
    # Check input/identity first, then update eligibility before deriving or
    # validating dependent values. Keep the final check after provenance too.
    _holds_generic_validate_blueprint(contract, blueprint, baseline)
    if "dateSerializationEvidence" in blueprint:
        if baseline is None or "_holds_date_serialization_evidence" not in globals():
            raise AdapterError("Date serialization evidence requires its qualified baseline and reviewed date extension.")
        if blueprint["dateSerializationEvidence"] != _holds_date_serialization_evidence(contract, baseline, blueprint):
            raise AdapterError("Date serialization evidence differs from independent baseline/request derivation.")
    _holds_validate_update_restrictions(contract, blueprint, baseline)
    # Rederive before delegating to existing scalar and generic validators.
    expected_defaults = []
    for operation in blueprint.get("operations", []):
        intermediate_hash = operation.get("requiredIntermediateValueSha256")
        if intermediate_hash is not None:
            if not isinstance(intermediate_hash, str) or re.fullmatch(r"[0-9a-f]{64}", intermediate_hash) is None:
                raise AdapterError("Recovery stage requires an exact SHA-256 intermediate value binding.")
            if baseline is not None:
                entity = _entity_map(contract)[operation["entity"]]
                intermediate = _row_index(baseline, entity).get(_target_tuple(entity, operation["targetKey"]))
                if intermediate is None or _holds_value_hash(entity, intermediate) != intermediate_hash:
                    raise AdapterError("Intermediate recovery readback differs; stop and replan, never apply the stale next stage.")
        requested = operation.get("requestedValues")
        has_manual = _HOLDS_MANUAL in operation.get("values", {})
        if operation.get("action") == "create":
            if requested is None:
                if _HOLDS_DERIVED_KEYS.intersection(operation):
                    raise AdapterError("Incomplete create source-effect provenance.")
                if baseline is not None:
                    raise AdapterError("Create design requires normalization with independently derived source effects before building.")
                _holds_validate_create_defaults(_entity_map(contract)[operation["entity"]])
                continue  # An intent-only shape check; canonical build requires provenance.
            if not isinstance(requested, dict):
                raise AdapterError("Create requestedValues must retain the original explicit inputs.")
            if "baselineValueSha256" in operation or intermediate_hash is not None:
                raise AdapterError("Create has no original target row; baseline/recovery target hashes are invalid.")
            entity = _entity_map(contract)[operation["entity"]]
            for field, value in requested.items():
                _validate_field_value(entity, field, value, operation["id"])
            defaulted, receipts = _holds_defaulted_create_values(contract, operation, requested)
            expected_defaults.extend(receipts)
            values, effects = _holds_create_materialization(defaulted, operation=operation)
            if (operation.get("values") != values or operation.get("sourceDrivenEffects") != effects
                    or operation.get("potentialSourceDrivenEffects") != _holds_potential_effects(values, create=True)):
                raise AdapterError("Create materialized values or effects differ from independent source derivation.")
            notice = _holds_create_setter_notice(operation)
            if notice is not None and notice not in blueprint.get("warnings", []):
                raise AdapterError("Create nonblocking source-effect disclosure is missing or differs from independent derivation.")
            notice = _holds_create_lookup_notice(operation)
            if notice is not None and notice not in blueprint.get("warnings", []):
                raise AdapterError("Create nonblocking lookup-maintenance disclosure is missing or differs from independent derivation.")
            continue
        if requested is None:
            if (_HOLDS_DERIVED_KEYS - {"accountingEffects"}).intersection(operation):
                raise AdapterError("Incomplete manual-release effect provenance.")
            if has_manual and baseline is not None:
                raise AdapterError("Manual-release design requires baseline-bound normalization before building.")
            if baseline is not None:
                entity = _entity_map(contract)[operation["entity"]]
                before = _row_index(baseline, entity).get(_target_tuple(entity, operation["targetKey"]))
                required = _holds_validate_import_consistency(operation["values"], before=before, operation=operation)
                if any(operation["values"].get(field, (before or {}).get(field)) != value
                       for field, value in required.items()):
                    raise AdapterError("Routing-off design requires baseline-bound normalization before building.")
            continue
        if not isinstance(requested, dict):
            raise AdapterError("Dependent-value requestedValues must retain the original explicit request.")
        if baseline is None:
            raise AdapterError("Baseline is required to validate manual-release source effects.")
        entity = _entity_map(contract)[operation["entity"]]
        before = _row_index(baseline, entity).get(_target_tuple(entity, operation["targetKey"]))
        if before is None:
            raise AdapterError("Manual-release target is missing from the qualified baseline.")
        for field, value in requested.items():
            _validate_field_value(entity, field, value, operation["id"])
        values, effects = _holds_manual_materialization(entity, before, requested, operation=operation)
        if (operation.get("values") != values or operation.get("sourceDrivenEffects") != effects
                or operation.get("potentialSourceDrivenEffects") != _holds_potential_effects(requested)
                or operation.get("baselineValueSha256") != _holds_value_hash(entity, before)):
            raise AdapterError("Manual-release materialized values, effects or baseline hash differ from independent source derivation.")
        notice = _holds_setter_notice(operation, before=before)
        if notice is not None and notice not in blueprint.get("warnings", []):
            raise AdapterError("Manual-release nonblocking source-effect disclosure is missing or differs from independent derivation.")
        # Equal scalar values must not suppress the explicitly requested full-row
        # candidate; importing it can maintain the supporting lookup.
    if blueprint.get("explicitDefaults", []) != expected_defaults:
        raise AdapterError("Create default provenance differs from independent omitted-input derivation.")
    _holds_validate_update_restrictions(contract, blueprint, baseline)
    _holds_validate_accounting_effects(contract, blueprint, baseline)
    _holds_scalar_validate_blueprint(contract, blueprint, baseline)


def _requirements(contract, blueprint):
    result = _holds_scalar_requirements(contract, blueprint)
    by_id = {operation["id"]: operation for operation in blueprint["operations"]}
    defaults = {(item["operationId"], item["field"]): item
                for item in blueprint.get("explicitDefaults", [])}
    for requirement in result:
        operation = by_id[requirement["operationId"]]
        if "requestedValues" not in operation:
            continue
        if requirement["kind"] == "value":
            field = requirement["field"]
            requested = field in operation["requestedValues"]
            derived = field in operation["sourceDrivenEffects"]
            default = defaults.get((operation["id"], field))
            requirement["valueRole"] = "requested-and-source-driven-effect" if requested and derived else (
                "requested" if requested else "source-driven-effect" if derived else "create-default")
            if derived:
                requirement["sourceIds"] = _holds_consistency_source_ids(operation)
                requirement["requirement"] = ("Persist the required pre-import consistency value "
                    + requirement["entity"] + "." + field + "=" + requirement["requestedValue"])
            elif default is not None:
                requirement["sourceIds"] = default["sourceIds"]
                requirement["requirement"] = ("Persist the recorded create default "
                    + requirement["entity"] + "." + field + "=" + requirement["requestedValue"])
        elif requirement["kind"] == "preserve_target":
            requirement["requirement"] = "Preserve every non-audit target value outside requested values and exact declared source-driven effects"
    entities = _entity_map(contract)
    for operation in blueprint["operations"]:
        if operation["action"] != "create":
            continue
        entity = entities[operation["entity"]]
        for field in entity["headers"]:
            if field in set(entity["keyFields"]) | set(entity["auditFields"]) | set(operation["values"]):
                continue
            result.append({"id": "REQ-%03d" % (len(result) + 1), "kind": "value",
                "operationId": operation["id"], "entity": entity["name"],
                "targetKey": operation["targetKey"], "field": field, "requestedValue": "",
                "valueRole": "omitted-optional-blank",
                "requirement": "Verify the omitted create field " + entity["name"] + "." + field
                    + " remains blank in the complete candidate and fresh export; no implicit default is assumed."})
    return result


def normalize_design(contract, baseline_path, request_path, design_path):
    baseline = _read_package(baseline_path, contract)
    blueprint = _holds_bind_manual_effects(contract, _normalized_blueprint(contract, _read_json(design_path)), baseline)
    if "_holds_date_serialization_evidence" in globals():
        blueprint["dateSerializationEvidence"] = _holds_date_serialization_evidence(contract, baseline, blueprint)
    _validate_blueprint(contract, blueprint, baseline)
    requirements = _requirements(contract, blueprint)
    preview = {"schemaVersion": SCHEMA_VERSION, "task": blueprint["task"],
        "requestSha256": _sha256_path(request_path), "designSha256": _sha256_bytes(_canonical_bytes(blueprint)),
        "baselineSha256": baseline.archive_sha256, "operations": [],
        "explicitDefaults": blueprint["explicitDefaults"], "prerequisites": blueprint["prerequisites"],
        "preservedValues": blueprint.get("preservedValues", []),
        "warnings": blueprint["warnings"], "evidenceUnresolvedUpdateOverrides": blueprint.get("evidenceUnresolvedUpdateOverrides", []),
        "requirementCount": len(requirements)}
    preview["inputPreflightReady"] = True
    preview["executionAuthorized"] = False
    for operation in blueprint["operations"]:
        item = {key: operation[key] for key in ("id", "action", "entity", "targetKey")}
        item.update(requestedValues=operation.get("requestedValues", operation["values"]),
            materializedValues=operation["values"], sourceDrivenEffects=operation.get("sourceDrivenEffects", {}),
            potentialSourceDrivenEffects=operation.get("potentialSourceDrivenEffects", {}),
            preserveOtherValues=operation.get("preserveOtherValues", True),
            preserveUnspecifiedRows=operation.get("preserveUnspecifiedRows", True))
        if "requestedValues" in operation:
            item["effectSourceIds"] = _holds_consistency_source_ids(operation)
            if "baselineValueSha256" in operation:
                item["baselineValueSha256"] = operation["baselineValueSha256"]
        if "requiredIntermediateValueSha256" in operation:
            item["requiredIntermediateValueSha256"] = operation["requiredIntermediateValueSha256"]
        if "accountingEffects" in operation:
            item["accountingEffects"] = operation["accountingEffects"]
        requested = operation.get("requestedValues", operation["values"])
        if (operation["action"] == "update" and operation["entity"] == "AP_HOLD_CODE"
                and _HOLDS_ACCOUNTING in requested):
            entity = _entity_map(contract)[operation["entity"]]
            before = _row_index(baseline, entity)[_target_tuple(entity, operation["targetKey"])]
            if before.get(_HOLDS_ACCOUNTING) == "X":
                preview["automaticRollbackSupported"] = False
                preview.setdefault("rollbackLimitations", []).append({
                    "operationId": operation["id"], "entity": operation["entity"],
                    "field": _HOLDS_ACCOUNTING,
                    "reason": "The original PostableFlag X is not an accepted input; automatic recovery cannot write it."})
        preview["operations"].append(item)
    if "_holds_date_normalization_evidence" in globals():
        preview["dateNormalizationEvidence"] = _holds_date_normalization_evidence(contract, {"baseline": baseline})
    if "dateSerializationEvidence" in blueprint:
        preview["dateSerializationEvidence"] = blueprint["dateSerializationEvidence"]
    return blueprint, preview, requirements


def validate_candidate(contract, template_path, baseline_path, blueprint_path, requirements_path, candidate_path):
    result = _holds_scalar_candidate_validate(contract, template_path, baseline_path,
        blueprint_path, requirements_path, candidate_path)
    blueprint = _read_json(blueprint_path)
    baseline = _read_package(baseline_path, contract)
    notices = []
    for operation in blueprint["operations"]:
        if operation["action"] == "create":
            notice = _holds_create_lookup_notice(operation)
            if notice is not None:
                notices.append(notice)
            notice = _holds_create_setter_notice(operation)
        else:
            notice = None
        if notice is not None:
            notices.append(notice)
        if operation["action"] == "update":
            entity = _entity_map(contract)[operation["entity"]]
            before = _row_index(baseline, entity)[_target_tuple(entity, operation["targetKey"])]
            notice = _holds_setter_notice(operation, before=before)
            if notice is not None:
                notices.append(notice)
            notice = _holds_update_lookup_notice(operation, before)
            if notice is not None:
                notices.append(notice)
            notice = _holds_accounting_notice(operation, before)
            if notice is not None:
                notices.append(notice)
    # Derive disclosures from the independently checked baseline and intent,
    # so stripping a copied warning cannot hide complete-row lookup maintenance.
    for notice in notices:
        if notice not in result["warnings"]:
            result["warnings"].append(notice)
    result["unresolvedWarnings"] = [warning for warning in result["unresolvedWarnings"]
                                    if warning not in notices]
    result["eligibleForDataLoaderValidation"] = (result["status"] == "PASS"
                                               and not result["unresolvedWarnings"])
    result["executionAuthorized"] = False
    accounting = [{"operationId": operation["id"], "entity": operation["entity"],
                   "targetKey": operation["targetKey"], **operation["accountingEffects"]}
                  for operation in blueprint["operations"] if operation.get("accountingEffects")]
    if accounting:
        result["accountingEffects"] = accounting
    if "_holds_date_serialization_evidence" in globals():
        # Derive this report field even when a direct synthetic blueprint omits
        # its optional provenance copy. Stripping metadata cannot hide a wire
        # representation change from candidate review.
        result["dateSerializationEvidence"] = _holds_date_serialization_evidence(contract, baseline, blueprint)
    return result


def reconcile(contract, baseline_path, candidate_path, blueprint_path, requirements_path, export_path):
    packages = {"baseline": _read_package(baseline_path, contract),
                "candidate": _read_package(candidate_path, contract),
                "persisted": _read_package(export_path, contract)}
    for label, package in packages.items():
        for identity in ("ProcessEnv", "ProcessRelease"):
            if package.metadata[identity] != packages["baseline"].metadata[identity]:
                raise AdapterError("Reconciliation " + label + " " + identity
                    + " differs from the qualified baseline; values from a different environment or release cannot prove this request.")
        if _schema_fingerprint(contract, package) != contract["package"]["schemaFingerprint"]:
            raise AdapterError("Reconciliation " + label + " schema fingerprint differs from the exact task contract.")
    result = _holds_scalar_reconcile(contract, baseline_path, candidate_path, blueprint_path, requirements_path, export_path)
    requirements = {item["id"]: item for item in _read_json(requirements_path)}
    for row in result["requirementMatrix"]:
        requirement = requirements[row["requirementId"]]
        if "valueRole" in requirement:
            row["valueRole"] = requirement["valueRole"]
            row["sourceIds"] = requirement.get("sourceIds", [])
        if requirement["kind"] == "preserve_target":
            row["detail"] = "Preservation checked outside requested values, exact declared source effects and audit fields."
    return result


def _holds_manual_recovery_plan(contract, before, current, forward):
    """Return a one-stage reverse or a staged plan; never submit either."""
    entities = _entity_map(contract)
    stages = [[], []]
    for index, operation in enumerate(forward["operations"], 1):
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        original = _row_index(before, entity).get(key)
        present = _row_index(current, entity).get(key)
        if original is None or present is None:
            raise AdapterError("Recovery target missing; obtain a qualified fresh export and replan.")
        expected = {**original, **operation["values"]}
        if _holds_value_hash(entity, present) != _holds_value_hash(entity, expected):
            raise AdapterError("Recovery readback differs from forward requested/effect/preservation expectations; stop and replan.")
        changed = {field: original[field] for field in operation["values"] if original[field] != present[field]}
        if not changed:
            continue
        conflicts = {}
        if present[_HOLDS_MANUAL] == "Y" and changed.get(_HOLDS_MANUAL) == "N":
            changed.update({field: original[field] for field in _HOLDS_MANUAL_EFFECTS})
            conflicts = {field: value for field, value in changed.items()
                         if field in _HOLDS_MANUAL_EFFECTS and value != _HOLDS_MANUAL_EFFECTS[field]}
        first_values = {_HOLDS_MANUAL: "N"} if conflicts else changed
        base = {"id": "RB-OP-%03d" % index, "action": "update", "entity": operation["entity"],
                "targetKey": operation["targetKey"], "preserveOtherValues": True, "preserveUnspecifiedRows": True}
        first = {**base, "values": first_values}
        _holds_validate_update_restrictions(contract, {"operations": [first]}, current)
        stages[0].append(first)
        if conflicts:
            materialized, _ = _holds_manual_materialization(entity, present, first_values)
            intermediate = {**present, **materialized}
            second = {field: original[field] for field in entity["updateFields"] if original[field] != intermediate[field]}
            stages[1].append({**base, "values": second,
                "requiredIntermediateValueSha256": _holds_value_hash(entity, intermediate)})
    return {"status": "STAGED_RECOVERY_REQUIRES_INTERMEDIATE_READBACK" if stages[1] else "ONE_STAGE_RECOVERY",
            "originalExportSha256": before.archive_sha256, "currentExportSha256": current.archive_sha256,
            "forwardDesignSha256": _sha256_bytes(_canonical_bytes(forward)),
            "stages": [{"ordinal": n + 1, "operations": operations} for n, operations in enumerate(stages) if operations],
            "nextAction": "Review stage 1 through ordinary design/candidate approval. After any server outcome, obtain a fresh exact-task export. Rebuild stage 2 only after its complete intermediate value hash matches; otherwise stop and replan. Each stage must also satisfy update restrictions and pre-import supplied-value consistency against its qualified current baseline; a matching hash does not grant eligibility. Stop on a restricted or conflicting change. Never submit or retry automatically.",
            "boundary": "Unqualified, conditional recovery plan; it may contain a restricted reverse. No atomic server rollback or bypass of task update restrictions or pre-import supplied-value consistency."}


def _all_updates_already_satisfied(contract, baseline, blueprint):
    # Full-row holds imports maintain the description lookup even when every
    # visible setup value is unchanged. Scalar equality does not prove no effect.
    return False


def make_rollback(contract, template_path, before_path, current_path, forward_blueprint_path,
                  rollback_blueprint_path, rollback_requirements_path, output_path):
    forward = _read_json(forward_blueprint_path)
    if any(operation.get("action") == "create" for operation in forward.get("operations", [])):
        raise AdapterError("Create has no exact automatic rollback: persisted setup rows cannot be deleted. "
            "A separately approved inactivation may be designed after fresh reconciliation; no recovery files were created.")
    if not any({_HOLDS_MANUAL, _HOLDS_ACCOUNTING}.intersection(
               operation.get("requestedValues", operation.get("values", {})))
               for operation in forward["operations"]):
        _validate_new_outputs([rollback_blueprint_path, rollback_requirements_path, output_path],
            [template_path, before_path, current_path, forward_blueprint_path])
        with tempfile.TemporaryDirectory(prefix="holds-recovery-") as temporary:
            folder = Path(temporary).resolve()
            staged_blueprint, staged_requirements, staged_zip = (
                folder / "blueprint.json", folder / "requirements.json", folder / "candidate.zip")
            report = _holds_scalar_rollback(contract, template_path, before_path, current_path,
                forward_blueprint_path, staged_blueprint, staged_requirements, staged_zip)
            rollback = _read_json(staged_blueprint)
            current = _read_package(current_path, contract)
            rollback["dateSerializationEvidence"] = _holds_date_serialization_evidence(contract, current, rollback)
            _validate_blueprint(contract, rollback, current)
            final_blueprint = folder / "final-blueprint.json"
            _write_json(final_blueprint, rollback)
            # Provenance is part of the design hash; the already generated ZIP
            # is unchanged and must independently revalidate against that design.
            report.update(validate_candidate(contract, template_path, current_path,
                final_blueprint, staged_requirements, staged_zip))
            report["dateSerializationEvidence"] = rollback["dateSerializationEvidence"]
            _publish_outputs({rollback_blueprint_path: final_blueprint.read_bytes(),
                rollback_requirements_path: staged_requirements.read_bytes(),
                output_path: staged_zip.read_bytes()})
        return _holds_lookup_recovery_boundary(report)
    before = _read_package(before_path, contract)
    current = _read_package(current_path, contract)
    for name in ("ProcessEnv", "ProcessRelease"):
        if before.metadata[name] != current.metadata[name]:
            raise AdapterError("Before and current recovery exports differ in " + name + ".")
    _validate_blueprint(contract, forward, before)
    policy = _holds_manual_recovery_plan(contract, before, current, forward)
    if policy["status"] != "ONE_STAGE_RECOVERY":
        # Existing CLI remains unchanged. Return the full deterministic plan in
        # the classified error; no misleading rollback ZIP or ready result.
        raise AdapterError("evidence_unresolved: recovery requires staged execution; " + json.dumps(policy, sort_keys=True))
    if not policy["stages"]:
        raise AdapterError("Recovery target already equals the original values; no candidate is needed.")
    _validate_new_outputs([rollback_blueprint_path, rollback_requirements_path, output_path],
        [template_path, before_path, current_path, forward_blueprint_path])
    design = {"operations": policy["stages"][0]["operations"],
              "resolvedScope": forward.get("resolvedScope", {})}
    rollback = _holds_bind_manual_effects(contract, _normalized_blueprint(contract, design), current)
    if "_holds_date_serialization_evidence" in globals():
        rollback["dateSerializationEvidence"] = _holds_date_serialization_evidence(contract, current, rollback)
    _validate_blueprint(contract, rollback, current)
    _write_json(rollback_blueprint_path, rollback)
    _write_json(rollback_requirements_path, _requirements(contract, rollback))
    report = build_candidate(contract, template_path, current_path, rollback_blueprint_path, rollback_requirements_path, output_path)
    report.update(rollbackOfDesignSha256=policy["forwardDesignSha256"],
                  rollbackScope="Restore original requested and source-driven collateral values after exact current-state reconciliation.")
    if any(operation.get("accountingEffects") for operation in rollback["operations"]):
        report["rollbackScope"] += (" Reverse PostableFlag updates restore the setup flag only; "
            "the accounting hook can run again and prior accounting-event state restoration is not guaranteed.")
        report["accountingEventStateRestorationGuaranteed"] = False
    if "dateSerializationEvidence" in rollback:
        report["dateSerializationEvidence"] = rollback["dateSerializationEvidence"]
    return _holds_lookup_recovery_boundary(report)


if __name__ == "__main__":
    raise SystemExit(main())
