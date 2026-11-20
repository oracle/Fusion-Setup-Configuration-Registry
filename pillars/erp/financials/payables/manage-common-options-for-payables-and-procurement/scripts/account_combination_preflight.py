#!/usr/bin/env python3
"""Run the read-only GL account-combination SOAP validation operation.

The command sends ``DynamicInsertion=No`` and cannot create a code combination.
Its envelope and response helpers are also used by the separately approved
creation command.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_combination_workflow as WORKFLOW  # noqa: E402


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
DEFAULT_PROPERTIES_PATH = REPOSITORY_ROOT / "core" / "auth" / "fusionEnv.properties"
MAX_RESPONSE_BYTES = 1024 * 1024
SOAP_FAULT_MESSAGE = "Fusion returned a SOAP fault; raw fault details omitted."


class PreflightError(RuntimeError):
    """A safe, actionable read-only preflight failure."""


def recovery_guidance(receipt: dict[str, object]) -> dict[str, object]:
    """Classify a no-create response without inferring account absence."""
    if receipt["valid"]:
        return {
            "outcome": "VALIDATED",
            "nextAction": "RESUME_AP_PREPARATION",
            "message": "Read-only account validation passed. Retain the receipt and resume AP preparation; do not create this combination again.",
        }
    if receipt["soapFault"] or not 200 <= receipt["httpStatus"] < 300:
        return {
            "outcome": "SERVICE_FAILURE",
            "nextAction": "RESOLVE_SERVICE_FAILURE",
            "message": "Account validation could not complete. Resolve the service or access failure and obtain a new read-only receipt; this is not evidence that the account is missing.",
        }
    if receipt["responseFields"].get("Status") == ["Invalid"]:
        return {
            "outcome": "INVALID_COMBINATION",
            "nextAction": "REVIEW_ACCOUNT_RECOVERY",
            "choices": ["CORRECT_OR_USE_EXISTING_ACCOUNT", "REVIEW_APPROVED_CREATION", "STOP"],
            "message": "GL returned Invalid. This may mean a missing combination or another GL rule; absence and creation eligibility are unverified. Offer to correct or use an existing account, review separately approved creation, or stop. Honor any prohibition on GL creation. Never create automatically; after approved creation, verify with DynamicInsertion=No before resuming AP preparation.",
        }
    return {
        "outcome": "INCONCLUSIVE_RESPONSE",
        "nextAction": "RESOLVE_RESPONSE_FAILURE",
        "message": "GL did not return an unambiguous validation result. Retain the receipt and resolve the response failure before continuing; do not infer a missing account or initiate creation.",
    }


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def build_envelope(
    *, ledger_name: str, segments: list[str], dynamic_insertion: str = "No"
) -> bytes:
    if not 1 <= len(segments) <= 30 or any(not segment for segment in segments):
        raise PreflightError("One through 30 non-empty account segments are required.")
    if not ledger_name.strip():
        raise PreflightError("LedgerName is required.")
    if dynamic_insertion not in {"No", "Yes"}:
        raise PreflightError("DynamicInsertion must be exactly 'No' or 'Yes'.")

    envelope = ElementTree.Element(f"{{{SOAP_ENVELOPE_NAMESPACE}}}Envelope")
    body = ElementTree.SubElement(envelope, f"{{{SOAP_ENVELOPE_NAMESPACE}}}Body")
    operation = ElementTree.SubElement(body, f"{{{TYPES_NAMESPACE}}}validateAndCreateAccounts")
    row = ElementTree.SubElement(operation, f"{{{TYPES_NAMESPACE}}}validationInputRowList")

    values = [dynamic_insertion, *segments, ledger_name.strip()]
    names = ["DynamicInsertion", *[f"Segment{index}" for index in range(1, len(segments) + 1)], "LedgerName"]
    for name, value in zip(names, values, strict=True):
        child = ElementTree.SubElement(row, f"{{{SERVICE_NAMESPACE}}}{name}")
        child.text = value
    return ElementTree.tostring(envelope, encoding="utf-8", xml_declaration=True)


def response_summary(
    content: bytes,
    *,
    http_status: int,
    read_only: bool = True,
    dynamic_insertion: str = "No",
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
    summary = {
        "httpStatus": http_status,
        "readOnly": read_only,
        "dynamicInsertion": dynamic_insertion,
        "valid": valid,
        "soapFault": SOAP_FAULT_MESSAGE if fault_present else None,
        "responseFields": fields,
    }
    if read_only and dynamic_insertion == "No":
        summary["recovery"] = recovery_guidance(summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Fusion GL account-combination preflight.")
    parser.add_argument("--ledger-name", required=True)
    parser.add_argument("--segments", required=True, help="One through 30 hyphen-delimited segment values.")
    parser.add_argument("--properties", default=str(DEFAULT_PROPERTIES_PATH))
    parser.add_argument("--output", help="Write the sanitized validation receipt as JSON.")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--callback-timeout", type=int, default=60)
    parser.add_argument("--token-cache")
    parser.add_argument("--force-login", action="store_true")
    parser.add_argument("--no-open-browser", action="store_false", dest="open_browser", default=True)
    args = parser.parse_args(argv)

    segments = args.segments.split("-")
    envelope = build_envelope(ledger_name=args.ledger_name, segments=segments)
    receipt = WORKFLOW.execute(
        WORKFLOW.load_environment(Path(args.properties)),
        endpoint=SERVICE_PATH, soap_action=VALIDATE_SOAP_ACTION,
        operation="validateAndCreateAccounts", envelope=envelope, read_only=True,
        business_context={"ledgerName": args.ledger_name.strip(), "segments": segments,
                          "dynamicInsertion": "No"},
        summarize=response_summary, output=Path(args.output) if args.output else None,
        protected_inputs=[Path(args.properties)], token_cache=args.token_cache,
        force_login=args.force_login, open_browser=args.open_browser,
        callback_timeout=args.callback_timeout, timeout=args.timeout,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        print(f"HTTP {receipt['httpStatus']}; wrote validation receipt to {args.output}")
    else:
        print(rendered, end="")
    if not receipt["valid"]:
        raise PreflightError(receipt["recovery"]["message"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WORKFLOW.AccountCombinationError as exc:
        print(f"Error [{exc.failure_class}]: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except (PreflightError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
