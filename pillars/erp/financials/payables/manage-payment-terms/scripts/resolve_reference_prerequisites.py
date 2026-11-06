#!/usr/bin/env python3
"""Read-only Calendar and Set Code preflight for Manage Payment Terms.

The preflight adds evidence to a copy of the requested design before the
offline adapter normalizes it. It never invents Calendar or SetCode values and
never writes to Fusion. Readable no-match and malformed responses block the
candidate; unavailable endpoints are recorded for later review.

Set Name and unspecified set input are also supported. Search by Set Name when
the user explicitly supplies a name; search both Set Code and Set Name when
the user says only "set". Read all result pages and require one distinct SetCode.
Keep an explicitly supplied code unchanged.

For an uploaded ZIP, check every SetCode and installment Calendar and save the
results with the archive SHA-256. The offline upload validator requires these
results whenever either reference is used.

If a supporting check is unavailable, preserve the supplied Calendar or SetCode
with a warning. If a SetCode must be found from a name or unspecified set,
an incomplete or unavailable lookup stops preparation; ask for the Set Code.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any

TASK_ROOT = Path(__file__).resolve().parents[1]
# Find the shared client instead of embedding credentials or another HTTP
# implementation in this task-local helper.
for candidate in (TASK_ROOT, *TASK_ROOT.parents):
    if (candidate / "core" / "data-loader" / "scripts" / "data_loader_metadata.py").is_file():
        ROOT = candidate
        break
else:
    raise RuntimeError("Could not locate the FSCR repository root.")
sys.path.insert(0, str(ROOT / "core" / "data-loader" / "scripts"))
import data_loader_metadata as metadata  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fsm_task_adapter import AdapterError, _validate_new_outputs, _write_new_json, _reference_target, _new_reference_provenance  # noqa: E402


class PreflightError(Exception):
    pass


def _items(payload: Any, required_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise PreflightError("resolver_failure: reference response does not contain an items array.")
    items = payload["items"]
    if any(not isinstance(item, dict) for item in items):
        raise PreflightError("resolver_failure: reference response contains a non-object item.")
    if any(any(field not in item for field in required_fields) for item in items):
        raise PreflightError("resolver_failure: reference response omits a requested field.")
    return items


def _url(host: str, path: str, fields: str, query: str) -> str:
    return host + path + "?" + urllib.parse.urlencode({
        "onlyData": "true", "fields": fields, "q": query,
    })


def _unavailable(error: metadata.DataLoadError) -> bool:
    return error.http_status is None or error.http_status in {400, 401, 403, 408, 429} or error.http_status >= 500


def _error_detail(error: metadata.DataLoadError) -> dict[str, str]:
    """Return a compact, already-redacted diagnostic from a loader error."""
    result = {"message": error.message}
    response = error.response
    if not isinstance(response, dict):
        return result
    details = response.get("o:errorDetails")
    if isinstance(details, list) and details and isinstance(details[0], dict):
        detail = details[0]
        if isinstance(detail.get("o:errorCode"), str):
            result["errorCode"] = detail["o:errorCode"]
        if isinstance(detail.get("detail"), str):
            result["detail"] = detail["detail"]
    elif isinstance(response.get("detail"), str):
        result["detail"] = response["detail"]
    return result


def _append_resolver_finding(
    design: dict[str, Any], *, operation_id: str, field: str, resolver: str,
    endpoint: str, requested_value: str, query: str, error: metadata.DataLoadError,
) -> None:
    findings = design.setdefault("resolverFindings", [])
    if not isinstance(findings, list):
        raise PreflightError("Design resolverFindings must be an array.")
    finding = {
        "classification": "resolver_contract_issue",
        "severity": "maintenance_required",
        "owner": "skill_maintainer",
        "actionRequired": "fix_or_reverify",
        "operationId": operation_id,
        "field": field,
        "resolver": resolver,
        "endpoint": endpoint,
        "httpStatus": error.http_status,
        "requestedValue": requested_value,
        "querySha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        "observedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "diagnostic": _error_detail(error),
    }
    if finding not in findings:
        findings.append(finding)


SET_PATH = "/fscmRestApi/resources/11.13.18.05/setIdSetsLOV"
SET_FIELDS = "SetCode,SetName,Description"


def _set_rows(config: dict[str, Any], field: str, value: str) -> list[dict[str, Any]]:
    """Read every result page before deciding whether a name is unambiguous."""
    escaped = value.replace("'", "''")
    query = f"{field}='{escaped}'"
    rows: list[dict[str, Any]] = []
    offset = 0
    for _ in range(100):
        url = _url(config["host"], SET_PATH, SET_FIELDS, query)
        payload = metadata.get_json(
            f"{url}&limit=500&offset={offset}", config["auth"], stage=f"validate {field}"
        )
        page = _items(payload, ("SetCode", "SetName", "Description"))
        if any(not isinstance(row["SetCode"], str) or not row["SetCode"].strip()
               or not isinstance(row["SetName"], str) for row in page):
            raise PreflightError("resolver_failure: set lookup returned an invalid code or name.")
        rows.extend(page)
        more = payload.get("hasMore", False)
        if not isinstance(more, bool):
            raise PreflightError("resolver_failure: set lookup has invalid pagination.")
        if not more:
            return rows
        if not page:
            raise PreflightError("resolver_failure: set lookup pagination made no progress.")
        offset += len(page)
    raise PreflightError("resolver_failure: set lookup exceeded its page limit.")


def _resolve_set(operation: dict[str, Any], resolved: dict[str, Any],
                 config: dict[str, Any], summary: dict[str, int]) -> None:
    target, values = operation.get("targetKey", {}), operation["values"]
    supplied_codes = [container["SetCode"] for container in (target, values)
                      if container.get("SetCode") not in (None, "")]
    if len(supplied_codes) == 2 and supplied_codes[0] != supplied_codes[1]:
        raise PreflightError("input_validation: conflicting SetCode values; ask the user which code to use.")
    supplied_code = supplied_codes[0] if supplied_codes else None
    reference = operation.get("setReference")
    if reference is None:
        if supplied_code is None:
            return
        kind, value = "code", supplied_code
    else:
        if (not isinstance(reference, dict)
                or reference.get("kind") not in {"code", "name", "unspecified"}
                or not isinstance(reference.get("value"), str)
                or not reference["value"].strip()):
            raise PreflightError("input_validation: setReference needs kind code, name, or unspecified and a nonblank value.")
        kind, value = reference["kind"], reference["value"]
    if not isinstance(value, str) or not value.strip():
        raise PreflightError("input_validation: supply a nonblank set code or name.")
    if kind == "code" and supplied_code is not None and value != supplied_code:
        raise PreflightError("input_validation: set code and setReference disagree; ask the user which code to use.")
    fields = ("SetCode",) if kind == "code" else (("SetName",) if kind == "name" else ("SetCode", "SetName"))
    matches: list[dict[str, Any]] = []
    operation_id = str(operation.get("id", "<unnamed>"))
    for field in fields:
        try:
            matches.extend(_set_rows(config, field, value))
        except metadata.DataLoadError as exc:
            if not _unavailable(exc):
                raise PreflightError(f"resolver_failure: cannot look up the set: {exc.message}") from exc
            if kind != "code":
                raise PreflightError(
                    "resolution_required: cannot finish the set lookup. "
                    "Please supply the Set Code; a name or unspecified set cannot be used without a complete lookup."
                ) from exc
            if exc.http_status == 400:
                _append_resolver_finding(
                    resolved, operation_id=operation_id, field="SetCode", resolver="validate_set_code",
                    endpoint=SET_PATH, requested_value=value,
                    query="SetCode='" + value.replace("'", "''") + "'", error=exc,
                )
                summary["resolverContractIssues"] += 1
                resolved["warnings"].append(
                    "Set Code check returned HTTP 400; preserving the supplied code and recording a resolver_contract_issue."
                )
            else:
                resolved["warnings"].append(
                    "Set Code check could not run. The supplied code is unchanged; Fusion must check it during the approved import."
                )
            resolved.setdefault("referenceDiagnostics", []).append({
                "SetCode": value, "endpoint": SET_PATH, "httpStatus": exc.http_status,
                "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                "diagnostic": _error_detail(exc),
            })
            summary["validationSkipped"] += 1
            status, code, name = "validation_skipped", value, None
            break
    else:
        if not matches:
            raise PreflightError(f"not_found: no set matched {value!r}; stop before ZIP/import.")
        by_code = {row["SetCode"]: row for row in matches}
        if kind != "code" and len(by_code) != 1:
            choices = [{"SetCode": row["SetCode"], "SetName": row["SetName"]}
                       for row in by_code.values()]
            raise PreflightError(
                "ambiguous_set: more than one set matches. Ask the user to choose: "
                + json.dumps(choices, ensure_ascii=False)
            )
        if kind == "code":
            # An explicit code remains unchanged. The API response corroborates it;
            # it does not authorize replacing it or choosing a different code.
            status, code, name = "validated", value, None
        else:
            selected = next(iter(by_code.values()))
            status, code, name = "resolved", selected["SetCode"], selected["SetName"]
        summary["satisfied"] += 1
    if supplied_code is not None and supplied_code != code:
        raise PreflightError("input_validation: supplied Set Code and resolved Set Name identify different sets; ask the user to choose.")
    if reference is not None:
        operation.setdefault("targetKey", {})["SetCode"] = code
        if "SetCode" in values:
            values.pop("SetCode")
        operation["setResolution"] = {
            "kind": kind, "suppliedValue": value, "SetCode": code,
            "SetName": name, "status": status, "searchedFields": list(fields),
            "provenance": _new_reference_provenance(resolved.get("referenceContext")),
            "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        }


def _configured_reference_target(config: dict[str, Any], selected: Any = None,
                                 baseline: Any = None) -> dict[str, str]:
    """Bind the selected Fusion identity to the configured authenticated origin.

    OAuth's environment is a profile label, not a Fusion ProcessEnv. An
    independent referenceContext may select the latter; never infer it from
    a ZIP, a receipt, a profile suffix, or the hostname.
    """
    configured = _reference_target({"environment": config.get("environment"),
                                    "baseUrl": config.get("host")})
    explicit = config.get("referenceContext")
    if explicit is not None:
        actual = _reference_target(explicit, baseline)
        if selected is not None and _reference_target(selected, baseline) != actual:
            raise AdapterError("REFERENCE_PROVENANCE: conflicting selected referenceContext values.")
    else:
        actual = _reference_target(selected if selected is not None else configured, baseline)
    if actual["baseUrl"] != configured["baseUrl"]:
        raise AdapterError("REFERENCE_PROVENANCE: selected referenceContext origin differs from the configured target.")
    return actual


def resolve(design: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    resolved = copy.deepcopy(design)
    actual = _configured_reference_target(config, design.get("referenceContext"))
    resolved["referenceContext"] = actual
    operations = resolved.get("operations")
    if not isinstance(operations, list) or not operations:
        raise PreflightError("Design must contain a nonempty operations array.")
    warnings = resolved.setdefault("warnings", [])
    if not isinstance(warnings, list):
        raise PreflightError("Design warnings must be an array.")
    summary = {"satisfied": 0, "validationSkipped": 0, "unresolved": 0, "resolverContractIssues": 0}
    checks = {
        "Calendar": (
            "validate_payables_calendar",
            "/fscmRestApi/resources/11.13.18.05/payablesCalendarTypes",
            "calendarName,calendarType", "calendarName", "PAYMENT TERMS",
        ),
    }
    for operation in operations:
        if not isinstance(operation, dict) or not isinstance(operation.get("values"), dict):
            raise PreflightError("Each operation must contain a values object.")
        target_key = operation.get("targetKey", {})
        if not isinstance(target_key, dict):
            raise PreflightError("Each operation targetKey must be an object when supplied.")
        operation_id = str(operation.get("id", "<unnamed>"))
        _resolve_set(operation, resolved, config, summary)
        for field, (resolver, path, fields, response_field, type_value) in checks.items():
            # Calendar is a line value, while SetCode is part of the
            # subscription's source-backed alternate key. Check both
            # locations so a requested subscription is never skipped.
            raw_value = operation["values"].get(field, target_key.get(field))
            if raw_value is None:
                continue
            value = str(raw_value).strip()
            if not value:
                continue
            escaped_value = value.replace("'", "''")
            query = f"{response_field}='{escaped_value}'"
            if type_value:
                query += f" and calendarType='{type_value}'"
            try:
                response = metadata.get_json(_url(config["host"], path, fields, query), config["auth"], stage=f"validate {field}")
            except metadata.DataLoadError as exc:
                if not _unavailable(exc):
                    raise PreflightError(f"resolver_failure: cannot validate {field}: {exc.message}") from exc
                if exc.http_status == 400:
                    _append_resolver_finding(
                        resolved, operation_id=operation_id, field=field, resolver=resolver,
                        endpoint=path, requested_value=value, query=query, error=exc,
                    )
                    warnings.append(
                        f"Read-only {field} validation returned HTTP 400; preserving the requested "
                        "value for Fusion import and recording a resolver_contract_issue for skill maintenance."
                    )
                    summary["resolverContractIssues"] += 1
                else:
                    warnings.append(f"Read-only {field} validation skipped because the endpoint was unavailable; Fusion import remains authoritative.")
                resolved.setdefault("referenceDiagnostics", []).append({
                    field: raw_value, "endpoint": path, "httpStatus": exc.http_status,
                    "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "diagnostic": _error_detail(exc),
                })
                summary["validationSkipped"] += 1
                continue
            # This supporting GET is corroborating evidence, not the FSM
            # resolver.  The query already expresses the submitted criteria;
            # once it yields a readable record, leave any final identity or
            # case decision to FSM Import.
            required_fields = tuple(part.strip() for part in fields.split(","))
            matches = _items(response, required_fields)
            if not matches:
                raise PreflightError(
                    f"not_found: read-only {field} validation returned no rows for "
                    f"{value!r}; candidate generation is blocked."
                )
            summary["satisfied"] += 1
    return resolved, summary


def resolve_uploaded_package(package_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Check uploaded SetCodes and installment Calendars without changing the archive."""
    import fsm_task_adapter as adapter

    contract = adapter._load_contract(TASK_ROOT / "e2e-adapter.json")
    package = adapter._read_package(package_path, contract)
    actual = _configured_reference_target(config, baseline=package)
    checks = []
    references = [
        ("SetCode", value, SET_PATH)
        for value in sorted({row["SetCode"] for row in package.rows["AP_TERM_SUBSCRIPTION"]})
    ] + [
        ("Calendar", value, "/fscmRestApi/resources/11.13.18.05/payablesCalendarTypes")
        for value in sorted({row["Calendar"] for row in package.rows["AP_TERM_LINE"]
                             if row["Calendar"].strip()})
    ]
    for field, value, endpoint in references:
        check = {
            field: value, "endpoint": endpoint,
            "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        design = {"operations": [{
            "id": "UPLOAD-REFERENCE", "action": "create",
            "entity": "AP_TERM_SUBSCRIPTION" if field == "SetCode" else "AP_TERM_LINE",
            "targetKey": {"SetCode": value} if field == "SetCode" else {},
            "values": {"Calendar": value} if field == "Calendar" else {},
        }]}
        try:
            resolved, summary = resolve(design, config)
            check.update(status="validation_skipped" if summary["validationSkipped"] else "validated",
                         warnings=resolved["warnings"], resolverFindings=resolved.get("resolverFindings", []),
                         diagnostics=resolved.get("referenceDiagnostics", []))
        except PreflightError as exc:
            check.update(status="FAIL", error=str(exc))
        checks.append(check)
    return {"schemaVersion": "payment-terms-upload-reference-v1",
            "status": "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS",
            "uploadedPackageSha256": package.archive_sha256,
            **actual, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--design", type=Path)
    source.add_argument("--package", type=Path, help="Check SetCodes and installment Calendars in an unchanged uploaded FSM ZIP.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-context", type=Path, help="Independently selected Fusion environment and baseUrl JSON; distinct from the OAuth profile name.")
    metadata.add_oauth_arguments(parser)
    args = parser.parse_args(argv)
    try:
        _validate_new_outputs([args.output], [value for key, value in vars(args).items()
                                             if key != "output" and isinstance(value, Path)])
        design = json.loads(args.design.read_text(encoding="utf-8")) if args.design else None
        config = metadata.read_config(args.properties, **metadata.oauth_kwargs(args))
        if args.reference_context:
            config["referenceContext"] = json.loads(args.reference_context.read_text(encoding="utf-8"))
        if args.package:
            resolved = resolve_uploaded_package(args.package, config)
            summary = {"status": resolved["status"]}
        else:
            resolved, summary = resolve(design, config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        _write_new_json(args.output, resolved)
        print(json.dumps({"status": "PASS", **summary}, sort_keys=True))
        return 1 if resolved.get("status") == "FAIL" else 0
    except (AdapterError, OSError, ValueError, PreflightError, metadata.DataLoadError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
