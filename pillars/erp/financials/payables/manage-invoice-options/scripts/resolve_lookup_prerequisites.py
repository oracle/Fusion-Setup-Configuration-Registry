#!/usr/bin/env python3
"""Resolve Invoice Options lookup-code prerequisites through Financials REST.

This is a live, read-only preflight that runs before ``fsm_task_adapter.py
normalize``.  The adapter remains deliberately offline: this helper adds the
normalized prerequisite receipt that the adapter validates.

If the caller cannot use a supporting lookup resource (for example, HTTP
401/403), or the resource returns multiple records, the helper records an
explicit advisory ``validation_skipped`` receipt and leaves Fusion import as
the authority. A readable zero-result is conclusive: it blocks candidate
creation. Create-time BU/ledger derivation and interest-account validation are blocking.
Account validation uses the task-owned read-only GL helper and never creates
a combination. Its ledger and ordered segments must match the fresh baseline
plus requested delta; an existing CCID is required.

Reading guide: URL helpers create the supported read-only queries, resolver
functions add receipts to a copy of the design, and ``main`` writes that
resolved design. No helper in this file performs a Fusion write.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import re
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any


TASK_ROOT = Path(__file__).resolve().parents[1]


def _repository_root() -> Path:
    for candidate in (TASK_ROOT, *TASK_ROOT.parents):
        if (candidate / "core" / "data-loader" / "scripts" / "data_loader_metadata.py").is_file():
            return candidate
    raise RuntimeError("Could not locate the FSCR repository root.")


REPOSITORY_ROOT = _repository_root()
DATA_LOADER_SCRIPTS = REPOSITORY_ROOT / "core" / "data-loader" / "scripts"
if str(DATA_LOADER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(DATA_LOADER_SCRIPTS))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import data_loader_metadata as metadata  # noqa: E402
from fsm_task_adapter import (  # noqa: E402
    AdapterError,
    _validate_new_outputs,
    _write_new_json,
    _reference_target,
    _new_reference_provenance,
    _interest_account_context,
    _load_contract,
    _read_package,
    CURRENCY_RECEIPT_CONTRACTS,
    LOOKUP_RECEIPT_CONTRACTS,
    PAYMENT_TERM_RECEIPT_FIELDS,
    SYSTEM_LOOKUP_CODES,
)


PAYMENT_TERMS_PATH = "/fscmRestApi/resources/11.13.18.05/payablesPaymentTerms"
CURRENCIES_PATH = "/fscmRestApi/resources/11.13.18.05/currenciesLOV"
BUSINESS_UNITS_PATH = "/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV"
LEDGERS_PATH = "/fscmRestApi/resources/11.13.18.05/ledgersLOV"
# Hard limits apply to the complete lookup, independently of per-GET timeouts.
PAYMENT_TERM_MAX_PAGES = 100
PAYMENT_TERM_MAX_ROWS = 10_000
ADVISORY_UNAVAILABLE_STATUSES = frozenset({400, 401, 403, 408, 429})


class LookupPreflightError(Exception):
    """A readable lookup result cannot support the requested design."""


class LookupPaginationError(LookupPreflightError):
    """Incomplete resolver results must never produce a lookup receipt."""

    classification = "resolver_pagination_incomplete"
    failure_class = "Fusion API"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LookupPreflightError(f"Cannot read design JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise LookupPreflightError("Design JSON must contain one object.")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_new_json(path, payload)


def _is_advisory_unavailable(error: metadata.DataLoadError) -> bool:
    """Return true only for unavailable/authentication read preflight states."""
    status = error.http_status
    return status is None or status in ADVISORY_UNAVAILABLE_STATUSES or status >= 500


# These functions build requests only. HTTP execution is delegated to the
# central Data Loader client so authentication stays outside this task script.
def _payment_term_url(host: str, name: str, offset: int = 0) -> str:
    return host + PAYMENT_TERMS_PATH + "?" + urllib.parse.urlencode(
        {"onlyData": "true", "fields": "name,termsId", "q": f"name='{name}'",
         **({"offset": str(offset)} if offset else {})}
    )


def _payment_term_rows(config: dict[str, Any], name: str, field: str) -> list[dict[str, Any]]:
    """Stop on a valid matching page; bound any search needed to find it."""
    matching_rows: list[dict[str, Any]] = []
    offset = 0
    for _ in range(PAYMENT_TERM_MAX_PAGES):
        response = metadata.get_json(
            _payment_term_url(config["host"], name, offset), config["auth"],
            stage=f"validate {field} payment term",
        )
        page = _items(response)
        if len(page) != len(response["items"]):
            raise LookupPreflightError("Payment-term response contains a malformed record.")
        has_more = response.get("hasMore", False)
        if type(has_more) is not bool or (has_more and not page):
            raise LookupPaginationError("Payment-term pagination is malformed or did not advance; candidate generation is blocked.")
        for key, expected in (("offset", offset), ("count", len(page))):
            if key in response and (type(response[key]) is not int or response[key] != expected):
                raise LookupPaginationError("Payment-term pagination reports an inconsistent offset or count; candidate generation is blocked.")
        if offset + len(page) > PAYMENT_TERM_MAX_ROWS:
            raise LookupPaginationError("Payment-term pagination exceeded the row limit; candidate generation is blocked.")
        matches = [row for row in page if isinstance(row.get("name"), str)
                   and row["name"].strip().casefold() == name.strip().casefold()]
        if any(_payment_term_identity([row]) == (1, True) for row in matches):
            # This GET corroborates the supplied name. It does not need to
            # establish uniqueness; FSM performs final resolution at import.
            # Retain the observed page for existing ambiguity diagnostics.
            return page
        matching_rows.extend(matches)
        if not has_more:
            return matching_rows
        # Advance by every consumed row, including nonmatching records.
        # Identical projected contents do not prove that a page is stuck.
        offset += len(page)
    raise LookupPaginationError("Payment-term pagination exceeded the page limit; candidate generation is blocked.")


def _payment_term_identity(rows: list[dict[str, Any]]) -> tuple[int, bool]:
    """Assess IDs and names in observed rows, without proving global uniqueness.

    IDs corroborate the lookup only. Never substitute one into the FSM request.
    """
    identities: set[str] = set()
    names: set[str] = set()
    complete = True
    for row in rows:
        identifier = row.get("termsId")
        valid_id = (
            isinstance(identifier, int) and not isinstance(identifier, bool) and identifier > 0
        ) or (
            isinstance(identifier, str) and identifier.isascii()
            and identifier.isdecimal() and int(identifier) > 0
        )
        if valid_id:
            identities.add(str(int(identifier)))
        else:
            complete = False
        returned_name = row.get("name")
        if isinstance(returned_name, str) and returned_name.strip():
            names.add(returned_name)
        else:
            complete = False
    return len(identities), complete and len(names) == 1


def _currency_url(host: str, code: str) -> str:
    return host + CURRENCIES_PATH + "?" + urllib.parse.urlencode(
        {"finder": f"CurrencyCodeAllRowsFinder;CurrencyCode={code}"}
    )


def _business_unit_url(host: str, name: str) -> str:
    return host + BUSINESS_UNITS_PATH + "?" + urllib.parse.urlencode({
        "onlyData": "true", "fields": "BusinessUnitId,BusinessUnitName,ActiveFlag,PrimaryLedgerId",
        "q": f"BusinessUnitName='{name}'",
    })


def _ledger_url(host: str, ledger_id: object) -> str:
    return host + LEDGERS_PATH + "/" + urllib.parse.quote(str(ledger_id)) + "?" + urllib.parse.urlencode(
        {"onlyData": "true", "fields": "LedgerId,Name,CurrencyCode"}
    )


def _items(response: Any) -> list[dict[str, Any]]:
    if not isinstance(response, dict):
        raise LookupPreflightError("Lookup response must be a JSON object.")
    values = response.get("items")
    if not isinstance(values, list):
        raise LookupPreflightError("Lookup response does not contain an items array.")
    return [item for item in values if isinstance(item, dict)]


def _upsert_prerequisite(design: dict[str, Any], prerequisite: dict[str, Any]) -> None:
    prerequisite["provenance"] = _new_reference_provenance(design.get("referenceContext"))
    existing = design.get("prerequisites", [])
    if not isinstance(existing, list):
        raise LookupPreflightError("Design prerequisites must be an array.")
    identity = tuple(prerequisite[key] for key in ("entity", "field", "resolver"))
    design["prerequisites"] = [
        item
        for item in existing
        if not (
            isinstance(item, dict)
            and tuple(item.get(key) for key in ("entity", "field", "resolver")) == identity
        )
    ] + [prerequisite]


def _append_warning(design: dict[str, Any], warning: str) -> None:
    warnings = design.setdefault("warnings", [])
    if not isinstance(warnings, list):
        raise LookupPreflightError("Design warnings must be an array.")
    if warning not in warnings:
        warnings.append(warning)


def _append_resolver_contract_issue(
    design: dict[str, Any], *, operation_id: str, field: str, resolver: str,
    endpoint: str, requested_value: str, error: metadata.DataLoadError,
) -> None:
    """Record a sanitized maintainer finding for an HTTP 400 preflight failure."""
    findings = design.setdefault("resolverFindings", [])
    if not isinstance(findings, list):
        raise LookupPreflightError("Design resolverFindings must be an array.")
    finding = {
        "classification": "resolver_contract_issue",
        "severity": "maintenance_required",
        "owner": "skill_maintainer",
        "actionRequired": "fix_or_reverify",
        "operationId": str(operation_id),
        "field": field,
        "resolver": resolver,
        "endpoint": endpoint,
        "httpStatus": 400,
        "requestedValue": requested_value,
        "querySha256": hashlib.sha256((endpoint + requested_value).encode("utf-8")).hexdigest(),
        "observedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "diagnostic": {"message": error.message},
    }
    if finding not in findings:
        findings.append(finding)


def _unavailable_receipt(
    design: dict[str, Any], *, entity: str, field: str, resolver: str,
    evidence: dict[str, Any], summary: dict[str, int],
) -> None:
    _upsert_prerequisite(design, {
        "entity": entity, "field": field, "resolver": resolver,
        "status": "validation_skipped", "evidence": {
            **evidence, "availability": "unavailable",
            "preflightPolicy": "advisory_on_unavailable",
        },
    })
    _append_warning(
        design,
        f"Read-only validation skipped for {field}; its Financials endpoint was unavailable. Fusion import remains authoritative.",
    )
    summary["validationSkipped"] += 1


def _multiple_results_receipt(
    design: dict[str, Any], *, entity: str, field: str, resolver: str,
    evidence: dict[str, Any], summary: dict[str, int],
) -> None:
    """Preserve an ambiguous readable response for authoritative FSM validation."""
    _upsert_prerequisite(design, {
        "entity": entity, "field": field, "resolver": resolver,
        "status": "validation_skipped", "evidence": {
            **evidence, "availability": "multiple_results",
            "preflightPolicy": "advisory_on_multiple_results",
        },
    })
    _append_warning(
        design,
        f"Read-only validation returned multiple records for {field}; preserving the submitted value for authoritative Fusion import validation.",
    )
    summary["validationSkipped"] += 1



def _run_account_validation(config: dict[str, Any], ledger: str, account: str) -> dict[str, Any]:
    """Use Invoice Options' read-only validator and the unchanged core client."""
    path = TASK_ROOT / "scripts/interest_account_validation.py"
    if not path.is_file():
        raise LookupPreflightError("Invoice Options account-combination validator is unavailable.")
    spec = importlib.util.spec_from_file_location("invoice_interest_account_validation", path)
    if spec is None or spec.loader is None:
        raise LookupPreflightError("Cannot load Invoice Options account-combination validator.")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    try:
        return helper.validate_existing_account(config["auth"], ledger, account)
    except (RuntimeError, ValueError) as exc:
        raise LookupPreflightError("GL account validation failed; candidate generation is blocked.") from exc


def _resolve_interest_account(
    design: dict[str, Any], config: dict[str, Any], operation: dict[str, Any],
    baseline: Any, summary: dict[str, int],
) -> None:
    entity = {"name": "AP_SYSTEM_PARAMETER", "keyFields": ["BuName"]}
    try:
        context = _interest_account_context(design, entity, operation, baseline)
    except AdapterError as exc:
        raise LookupPreflightError(str(exc)) from exc
    if context is None:
        return
    if baseline is None:
        raise LookupPreflightError(f"Operation {operation['id']} account preflight requires --baseline from a fresh task export.")
    account, ledger = context
    response = _run_account_validation(config, ledger, account)
    if not isinstance(response, dict):
        raise LookupPreflightError(f"Operation {operation['id']} GL response is malformed; import is blocked.")
    fields = response.get("responseFields", {})
    ccids = fields.get("CcId") if isinstance(fields, dict) else None
    if (response.get("valid") is not True or response.get("readOnly") is not True
            or response.get("dynamicInsertion") != "No" or response.get("soapFault")
            or type(response.get("httpStatus")) is not int or not 200 <= response["httpStatus"] < 300
            or not isinstance(fields, dict) or fields.get("Status") != ["Valid"] or not isinstance(ccids, list) or len(ccids) != 1
            or not isinstance(ccids[0], str) or re.fullmatch(r"[1-9][0-9]{0,37}", ccids[0]) is None):
        raise LookupPreflightError(f"Operation {operation['id']} InterestSegments is invalid or no existing CCID was confirmed; import is blocked.")
    receipt = {"operationId": operation["id"], "entity": operation["entity"], "field": "InterestSegments",
        "resolver": "validate_account_segments_read_only", "status": "satisfied",
        "targetKey": operation["targetKey"], "requestedValue": account, "ledgerName": ledger,
        "dynamicInsertion": "No", "readOnly": True, "valid": True,
        "httpStatus": response["httpStatus"], "ccid": ccids[0],
        "baselineSha256": baseline.archive_sha256, "evidence": response,
        "provenance": _new_reference_provenance(design.get("referenceContext"), baseline)}
    # Keep other operations' receipts; evidence is bound to one operation and BU.
    prior = design.setdefault("prerequisites", [])
    design["prerequisites"] = [item for item in prior if not (
        isinstance(item, dict) and item.get("operationId") == operation["id"]
        and item.get("entity") == operation["entity"] and item.get("field") == "InterestSegments"
        and item.get("resolver") == receipt["resolver"])] + [receipt]
    summary["satisfied"] += 1


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


def resolve_lookup_prerequisites(
    design: dict[str, Any], config: dict[str, Any], baseline: Any = None
) -> tuple[dict[str, Any], dict[str, int]]:
    """Return a design augmented with live or advisory lookup receipts."""
    resolved = copy.deepcopy(design)
    actual = _configured_reference_target(config, design.get("referenceContext"), baseline)
    resolved["referenceContext"] = actual
    operations = resolved.get("operations")
    if not isinstance(operations, list) or not operations:
        raise LookupPreflightError("Design must contain a nonempty operations array.")

    summary = {"satisfied": 0, "validationSkipped": 0}
    for position, operation in enumerate(operations, start=1):
        if not isinstance(operation, dict):
            raise LookupPreflightError("Each operation must be an object.")
        entity = operation.get("entity")
        values = operation.get("values")
        operation_id = operation.setdefault("id", f"OP-{position:03d}")
        operation.setdefault("action", "update")
        if not isinstance(entity, str) or not entity.strip() or not isinstance(values, dict):
            raise LookupPreflightError(
                f"Operation {operation_id} must contain entity and values objects."
            )
        for field, (resolver, lookup_type, allow_blank) in LOOKUP_RECEIPT_CONTRACTS.items():
            if field not in values:
                continue
            code = str(values[field]).strip()
            if allow_blank and not code:
                continue
            if not code:
                raise LookupPreflightError(
                    f"Operation {operation_id} supplies a blank required lookup code for {field}."
                )
            allowed_codes = SYSTEM_LOOKUP_CODES.get(lookup_type)
            if allowed_codes is not None:
                if code not in allowed_codes:
                    raise LookupPreflightError(
                        f"Operation {operation_id} {field} must use one of the supported "
                        f"system {lookup_type} codes: {', '.join(sorted(allowed_codes))}."
                    )
                summary["satisfied"] += 1
                continue
        # Live preflight portion of `resolve_business_unit_by_name_and_enterprise`:
        # resolve the active requested business unit and its primary ledger.
        # EnterpriseId resolution is completed locally by the task adapter.
        if operation.get("action", "update") == "create" and entity == "AP_SYSTEM_PARAMETER":
            target = operation.get("targetKey")
            bu_name = target.get("BuName") if isinstance(target, dict) else None
            if not isinstance(bu_name, str) or not bu_name.strip():
                raise LookupPreflightError(f"Operation {operation_id} create requires targetKey.BuName.")
            try:
                bu_rows = _items(metadata.get_json(
                    _business_unit_url(config["host"], bu_name), config["auth"],
                    stage="resolve invoice-options business unit",
                ))
                matches = [item for item in bu_rows if item.get("BusinessUnitName") == bu_name and item.get("ActiveFlag") is True]
                primary_ledger_ids = {str(item.get("PrimaryLedgerId", "")).strip() for item in matches}
                if not matches or "" in primary_ledger_ids or len(primary_ledger_ids) != 1:
                    raise LookupPreflightError(f"Operation {operation_id} requires active exact Business Unit rows with one shared primary ledger.")
                bu = matches[0]
                ledger = metadata.get_json(_ledger_url(config["host"], bu["PrimaryLedgerId"]), config["auth"], stage="resolve primary ledger")
                ledger_item = ledger if isinstance(ledger, dict) and "LedgerId" in ledger else (_items(ledger)[0] if len(_items(ledger)) == 1 else None)
                if not isinstance(ledger_item, dict) or not str(ledger_item.get("Name", "")).strip() or not str(ledger_item.get("CurrencyCode", "")).strip():
                    raise LookupPreflightError(f"Operation {operation_id} primary ledger result is incomplete.")
            except metadata.DataLoadError as exc:
                if exc.http_status == 400:
                    _append_resolver_contract_issue(
                        resolved, operation_id=operation_id, field="BuName",
                        resolver="resolve_business_unit_primary_ledger", endpoint=BUSINESS_UNITS_PATH,
                        requested_value=bu_name, error=exc,
                    )
                    _unavailable_receipt(
                        resolved, entity=entity, field="BuName",
                        resolver="resolve_business_unit_primary_ledger",
                        evidence={"buName": bu_name}, summary=summary,
                    )
                    # The adapter will later surface the missing required create
                    # context.  Do not discard the advisory receipt or its
                    # maintainer finding at this preflight stage.
                    continue
                raise LookupPreflightError(f"Operation {operation_id} cannot derive required BU primary-ledger values: {exc.message}") from exc
            scope = resolved.setdefault("resolvedScope", {})
            entries = scope.setdefault("businessUnits", []) if isinstance(scope, dict) else None
            if not isinstance(entries, list):
                raise LookupPreflightError("resolvedScope.businessUnits must be an array.")
            prior = next((item for item in entries if isinstance(item, dict) and item.get("entity") == entity and item.get("targetKey") == target), {})
            entry = {
                "entity": entity, "targetKey": target,
                "provenance": _new_reference_provenance(resolved["referenceContext"], baseline),
                "resolvedValues": {**(prior.get("resolvedValues", {}) if isinstance(prior, dict) else {}), "SOBName": ledger_item["Name"], "BaseCurrencyCode": ledger_item["CurrencyCode"]},
                "evidence": {**(prior.get("evidence", {}) if isinstance(prior, dict) else {}), "finBusinessUnitsLOV": {"source": "finBusinessUnitsLOV", "matchedBuName": bu_name, "businessUnitId": bu["BusinessUnitId"], "primaryLedgerId": bu["PrimaryLedgerId"], "resultCount": len(matches), "active": True}, "ledgersLOV": {"source": "ledgersLOV", "ledgerId": bu["PrimaryLedgerId"], "name": ledger_item["Name"], "currencyCode": ledger_item["CurrencyCode"]}},
            }
            entries[:] = [item for item in entries if not (isinstance(item, dict) and item.get("entity") == entity and item.get("targetKey") == target)] + [entry]
            summary["satisfied"] += 2
        if entity == "AP_SYSTEM_PARAMETER":
            _resolve_interest_account(resolved, config, operation, baseline, summary)
        # Implementation of the `resolve_payment_term_from_name` resolver
        # contract: create a read-only corroborating receipt for each supplied
        # payment-term name.  FSM import remains the authoritative resolver.
        for field in PAYMENT_TERM_RECEIPT_FIELDS:
            if field not in values:
                continue
            name = str(values[field]).strip()
            if not name:
                raise LookupPreflightError(f"Operation {operation_id} supplies blank {field}.")
            try:
                matches = _payment_term_rows(config, name, field)
            except metadata.DataLoadError as exc:
                if not _is_advisory_unavailable(exc):
                    raise LookupPreflightError(f"Operation {operation_id} cannot validate {field}: {exc.message}") from exc
                if exc.http_status == 400:
                    _append_resolver_contract_issue(
                        resolved, operation_id=operation_id, field=field,
                        resolver="resolve_payment_term_from_name", endpoint=PAYMENT_TERMS_PATH,
                        requested_value=name, error=exc,
                    )
                _unavailable_receipt(resolved, entity=entity, field=field,
                    resolver="resolve_payment_term_from_name",
                    evidence={"name": name}, summary=summary)
                continue
            # This query is corroborating evidence only.  It does not carry the
            # complete FSM import context, so do not impose a local case-sensitive
            # name comparison or select a term ID from its result set.
            if not matches:
                raise LookupPreflightError(
                    f"Operation {operation_id} {field} has no exact match in readable "
                    "payablesPaymentTerms results."
                )
            distinct_count, consistent = _payment_term_identity(matches)
            diagnostic = {
                "name": name, "returnedNames": [entry.get("name") for entry in matches],
                "termsIds": [entry.get("termsId") for entry in matches],
                "resultCount": len(matches), "distinctTermCount": distinct_count,
                "lookupPolicy": "first_valid_match", "uniquenessVerified": False,
                "source": "payablesPaymentTerms",
            }
            if distinct_count > 1:
                _multiple_results_receipt(resolved, entity=entity, field=field,
                    resolver="resolve_payment_term_from_name", evidence=diagnostic, summary=summary)
                continue
            if not consistent:
                _upsert_prerequisite(resolved, {
                    "entity": entity, "field": field,
                    "resolver": "resolve_payment_term_from_name",
                    "status": "validation_skipped", "evidence": {
                        **diagnostic, "availability": "unresolved_identity",
                        "preflightPolicy": "advisory_on_unresolved_identity",
                    },
                })
                _append_warning(resolved, f"Payment term {name} could not be corroborated because its observed reference IDs or names are incomplete or inconsistent; Fusion import will validate the supplied name.")
                summary["validationSkipped"] += 1
                continue
            item = matches[0]
            _upsert_prerequisite(resolved, {
                "entity": entity, "field": field,
                "resolver": "resolve_payment_term_from_name", "status": "satisfied",
                "evidence": {
                    "name": name,
                    "returnedNames": [entry.get("name") for entry in matches],
                    "termsId": item.get("termsId"),
                    "termsIds": [entry.get("termsId") for entry in matches],
                    "resultCount": len(matches),
                    "distinctTermCount": distinct_count,
                    "lookupPolicy": "first_valid_match", "uniquenessVerified": False,
                    "source": "payablesPaymentTerms"
                },
            })
            summary["satisfied"] += 1
        for field, resolver in CURRENCY_RECEIPT_CONTRACTS.items():
            if field not in values:
                continue
            code = str(values[field]).strip().upper()
            if not code:
                raise LookupPreflightError(f"Operation {operation_id} supplies blank {field}.")
            # Currency codes have a task-owned canonical representation.  Persist
            # it so the REST receipt and eventual FSM CSV use the same value.
            if isinstance(values[field], str):
                values[field] = code
            try:
                response = metadata.get_json(
                    _currency_url(config["host"], code), config["auth"],
                    stage=f"validate {field} currency",
                )
            except metadata.DataLoadError as exc:
                if not _is_advisory_unavailable(exc):
                    raise LookupPreflightError(f"Operation {operation_id} cannot validate {field}: {exc.message}") from exc
                if exc.http_status == 400:
                    _append_resolver_contract_issue(
                        resolved, operation_id=operation_id, field=field,
                        resolver=resolver, endpoint=CURRENCIES_PATH,
                        requested_value=code, error=exc,
                    )
                _unavailable_receipt(resolved, entity=entity, field=field,
                    resolver=resolver, evidence={"currencyCode": code}, summary=summary)
                continue
            # This is a corroborating preflight, not the context-aware FSM
            # resolver.  Retain readable currency results without requiring a
            # unique or case-exact local match.
            matches = _items(response)
            if not matches:
                raise LookupPreflightError(
                    f"Operation {operation_id} {field} has no exact match in readable "
                    "currenciesLOV results."
                )
            if len(matches) > 1:
                _multiple_results_receipt(resolved, entity=entity, field=field,
                    resolver=resolver, evidence={"currencyCode": code,
                        "returnedCurrencyCodes": [item.get("CurrencyCode", item.get("currencyCode")) for item in matches],
                        "resultCount": len(matches), "source": "currenciesLOV"}, summary=summary)
                continue
            _upsert_prerequisite(resolved, {
                "entity": entity, "field": field, "resolver": resolver,
                "status": "satisfied", "evidence": {
                    "currencyCode": code,
                    "returnedCurrencyCodes": [item.get("CurrencyCode", item.get("currencyCode")) for item in matches],
                    "resultCount": len(matches),
                    "source": "currenciesLOV",
                },
            })
            summary["satisfied"] += 1
    return resolved, summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True, help="Input request/design JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Resolved design JSON output.")
    parser.add_argument("--baseline", type=Path, help="Fresh Invoice Options export; required for account preflight.")
    parser.add_argument("--reference-context", type=Path, help="Independently selected Fusion environment and baseUrl JSON; distinct from the OAuth profile name.")
    metadata.add_oauth_arguments(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        _validate_new_outputs([args.output], [value for key, value in vars(args).items()
                                             if key != "output" and isinstance(value, Path)])
        config = metadata.read_config(args.properties, **metadata.oauth_kwargs(args))
        if args.reference_context:
            config["referenceContext"] = _read_json(args.reference_context)
        baseline = (_read_package(args.baseline, _load_contract(TASK_ROOT / "e2e-adapter.json"))
                    if args.baseline else None)
        resolved, summary = resolve_lookup_prerequisites(_read_json(args.design), config, baseline)
        _write_json(args.output, resolved)
        print(json.dumps({"status": "PASS", **summary, "output": str(args.output)}, sort_keys=True))
        return 0
    except (LookupPreflightError, AdapterError, metadata.DataLoadError, OSError) as exc:
        failure = {"status": "FAIL", "error": str(exc)}
        if hasattr(exc, "classification"):
            failure.update(classification=exc.classification, failureClass=exc.failure_class)
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
