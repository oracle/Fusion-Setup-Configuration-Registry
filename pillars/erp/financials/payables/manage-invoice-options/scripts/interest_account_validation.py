"""Invoice Options existing-account validation; never creates a GL combination.

Own the interest-account SOAP contract here. Authentication and HTTP are provided
by the unchanged core client. No dependency on the Common Options skill.
"""
from __future__ import annotations

from argparse import Namespace
import hashlib
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

CORE_ROOT = Path(__file__).resolve().parents[6] / "core"
sys.path.insert(0, str(CORE_ROOT / "fusion-api/ucm-rest-client/scripts"))
import ucm_rest_client as CORE_HTTP  # noqa: E402
from fsm_task_adapter import AdapterError, _canonical_account_segments  # noqa: E402


SOAP_ENVELOPE_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
TYPES_NAMESPACE = (
    "http://xmlns.oracle.com/apps/financials/generalLedger/accounts/"
    "codeCombinations/accountCombinationService/types/"
)
SERVICE_NAMESPACE = (
    "http://xmlns.oracle.com/apps/financials/generalLedger/accounts/"
    "codeCombinations/accountCombinationService/"
)
SERVICE_PATH = "/fscmService/AccountCombinationService"
VALIDATE_SOAP_ACTION = (
    "http://xmlns.oracle.com/apps/financials/generalLedger/accounts/"
    "codeCombinations/accountCombinationService/validateAndCreateAccounts"
)
MAX_RESPONSE_BYTES = 1024 * 1024
SOAP_FAULT_MESSAGE = "Fusion returned a SOAP fault; raw fault details omitted."


class PreflightError(RuntimeError):
    """A safe, actionable read-only preflight failure."""


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_segments(value: str) -> list[str]:
    """Use the same ordered account representation as the CSV adapter."""
    try:
        canonical = _canonical_account_segments(value)
    except AdapterError as exc:
        raise PreflightError(str(exc)) from exc
    if not canonical:
        raise PreflightError("One through 30 segment slots are required.")
    slots = canonical[:-1].split("\n")
    while slots and slots[-1] == "":
        slots.pop()
    return slots


def build_envelope(
    *, ledger_name: str, segments: list[str]
) -> bytes:
    if (not 1 <= len(segments) <= 30 or not any(segments)
            or any(not isinstance(segment, str) or segment != segment.strip()
                   or any(ord(char) < 32 for char in segment) for segment in segments)):
        raise PreflightError("One through 30 segment slots with a nonblank segment are required.")
    if not ledger_name.strip():
        raise PreflightError("LedgerName is required.")

    envelope = ElementTree.Element(f"{{{SOAP_ENVELOPE_NAMESPACE}}}Envelope")
    body = ElementTree.SubElement(envelope, f"{{{SOAP_ENVELOPE_NAMESPACE}}}Body")
    operation = ElementTree.SubElement(body, f"{{{TYPES_NAMESPACE}}}validateAndCreateAccounts")
    row = ElementTree.SubElement(operation, f"{{{TYPES_NAMESPACE}}}validationInputRowList")

    values = ["No", *segments, ledger_name.strip()]
    names = ["DynamicInsertion", *[f"Segment{index}" for index in range(1, len(segments) + 1)], "LedgerName"]
    for name, value in zip(names, values, strict=True):
        child = ElementTree.SubElement(row, f"{{{SERVICE_NAMESPACE}}}{name}")
        child.text = value
    return ElementTree.tostring(envelope, encoding="utf-8", xml_declaration=True)


def response_summary(
    content: bytes,
    *,
    http_status: int,
) -> dict[str, object]:
    if len(content) > MAX_RESPONSE_BYTES:
        raise PreflightError("Fusion SOAP response exceeds the permitted size.")
    if b"\x00" in content:
        raise PreflightError("Fusion SOAP response uses an unsupported encoding.")
    if b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
        raise PreflightError("Fusion SOAP response contains unsupported XML declarations.")
    try:
        root = ElementTree.fromstring(content)
    except (ElementTree.ParseError, LookupError, ValueError) as exc:
        raise PreflightError("Fusion returned invalid SOAP XML; response content omitted.") from exc

    # Interpret only the single operation/result submitted by this adapter.
    # Header fields, unrelated XML and other namespaces cannot prove validity.
    body_tag = f"{{{SOAP_ENVELOPE_NAMESPACE}}}Body"
    header_tag = f"{{{SOAP_ENVELOPE_NAMESPACE}}}Header"
    fault_tag = f"{{{SOAP_ENVELOPE_NAMESPACE}}}Fault"
    bodies = root.findall(body_tag)
    envelope_ok = (
        root.tag == f"{{{SOAP_ENVELOPE_NAMESPACE}}}Envelope"
        and len(bodies) == 1
        and len(root.findall(header_tag)) <= 1
        and all(child.tag in {body_tag, header_tag} for child in root)
    )
    body = bodies[0] if envelope_ok else None
    fault_present = body is not None and any(child.tag == fault_tag for child in body)
    result = None
    if body is not None and not fault_present and len(body) == 1:
        response = body[0]
        if (response.tag == f"{{{TYPES_NAMESPACE}}}validateAndCreateAccountsResponse"
                and len(response) == 1
                and response[0].tag == f"{{{TYPES_NAMESPACE}}}result"
                and response[0].get("{http://www.w3.org/2001/XMLSchema-instance}nil")
                not in {"true", "1"}):
            result = response[0]

    # Keep only bounded result fields. Free text never reaches the receipt.
    statuses: list[str] = []
    combination_ids: list[str] = []
    if result is not None:
        for tag, values in (("Status", statuses), ("CcId", combination_ids)):
            for element in result.findall(f"{{{SERVICE_NAMESPACE}}}{tag}"):
                # Nested values or nil/attributed leaves are not scalar results.
                values.append((element.text or "").strip()
                              if not len(element) and not element.attrib else "")
    fields: dict[str, list[str]] = {}
    if not fault_present:
        if len(statuses) == 1 and statuses[0].casefold() in {"valid", "invalid"}:
            fields["Status"] = [statuses[0].capitalize()]
        if (len(combination_ids) == 1
                and re.fullmatch(r"[1-9][0-9]{0,37}", combination_ids[0])):
            fields["CcId"] = combination_ids
    valid = (not fault_present and 200 <= http_status < 300
             and fields.get("Status") == ["Valid"])
    return {
        "httpStatus": http_status,
        "readOnly": True,
        "dynamicInsertion": "No",
        "valid": valid,
        "soapFault": SOAP_FAULT_MESSAGE if fault_present else None,
        "responseFields": fields,
    }



def validate_existing_account(auth: Any, ledger: str, account: str) -> dict[str, Any]:
    """Submit one fixed read-only GL validation through managed core OAuth."""
    if auth.explicit_access_token or auth.auth_code or auth.redirect_url:
        raise PreflightError("Account validation requires the managed OAuth session; use --token-cache.")
    props = auth.properties
    try:
        CORE_HTTP.require_props(props, ["environment", "restBaseUrl", "scope"])
        if any(not props[name].strip() for name in ("environment", "restBaseUrl", "scope")):
            raise ValueError("Blank environment identity.")
        base = props["restBaseUrl"].rstrip("/")
        origin = urllib.parse.urlsplit(base)
        origin.port
        if (origin.scheme != "https" or not origin.hostname or origin.username or origin.password
                or origin.query or origin.fragment or origin.path
                or any(c.isspace() or ord(c) < 32 for c in base)
                or auth.callback_timeout <= 0):
            raise ValueError("Invalid Fusion origin or callback timeout.")
    except (KeyError, ValueError, AttributeError, TypeError) as exc:
        raise PreflightError("Valid Fusion environment, HTTPS origin, OAuth scope and timeout are required.") from exc
    segments = parse_segments(account)
    envelope = build_envelope(ledger_name=ledger, segments=segments)
    options = Namespace(auth_mode="oauth", access_token=None, redirect_url=None,
                        auth_code=None, open_browser=auth.open_browser,
                        callback_timeout=auth.callback_timeout, token_cache=auth.token_cache,
                        force_login=auth.force_login, timeout=60)
    try:
        authorization = CORE_HTTP.get_authorization_header(props, options)
        content, _headers, status = CORE_HTTP.request_bytes(
            props, base + SERVICE_PATH, method="POST", authorization=authorization,
            body=envelope, headers={"Accept": "text/xml, application/soap+xml",
                "Content-Type": "text/xml; charset=UTF-8", "SOAPAction": VALIDATE_SOAP_ACTION},
            timeout=60)
    except (OSError, RuntimeError, ValueError) as exc:
        raise PreflightError("Core OAuth or GL SOAP validation failed; candidate generation is blocked.") from exc
    summary = response_summary(content, http_status=status)
    return {**summary, "schemaVersion": "fscr-soap-receipt-v1",
            "status": "RESPONSE_RECEIVED", "mayHaveApplied": False,
            "request": {"environment": props["environment"], "baseUrl": base,
                "endpointPath": SERVICE_PATH, "soapAction": VALIDATE_SOAP_ACTION,
                "operation": "validateAndCreateAccounts", "readOnly": True,
                "payloadSha256": hashlib.sha256(envelope).hexdigest(),
                "businessContext": {"ledgerName": ledger.strip(), "segments": segments,
                                    "dynamicInsertion": "No"}}}
