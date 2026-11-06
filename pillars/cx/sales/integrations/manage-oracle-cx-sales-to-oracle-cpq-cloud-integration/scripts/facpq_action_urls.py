#!/usr/bin/env python3
"""Construct the five FACPQ action URL values from a ready metadata manifest."""

from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path
from typing import Any


POSITIVE_ID_FIELDS = (
    "documentId",
    "copyActionId",
    "versionActionId",
)
REQUIRED_FIELDS = (
    "faHostUrl",
    "facpqEndpointUrl",
    "restFrameworkVersion",
    "processName",
    "documentName",
    *POSITIVE_ID_FIELDS,
)
VARIABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
REST_VERSION = re.compile(r"^v[0-9]+$")
EXPECTED_CONSUMER = (
    "cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration"
)


class ContractError(ValueError):
    """Manifest or URL-contract validation failure."""


def load_ready_manifest(path_value: str) -> dict[str, str]:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise ContractError(f"Metadata manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("Metadata manifest must be a readable JSON object.") from exc
    if not isinstance(payload, dict):
        raise ContractError("Metadata manifest must be a JSON object.")
    if payload.get("status") != "ready" or payload.get("completeness") != "complete":
        raise ContractError("Metadata manifest must have status ready and completeness complete.")
    boundaries = payload.get("boundaries")
    if (
        not isinstance(boundaries, dict)
        or boundaries.get("facpq_mutations") is not False
        or boundaries.get("allowed_facpq_methods") != ["GET"]
        or boundaries.get("bm_cpq_supported") is not False
        or boundaries.get("consumer") != EXPECTED_CONSUMER
    ):
        raise ContractError(
            "Metadata manifest must declare a GET-only FACPQ boundary with BM CPQ disabled."
        )
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise ContractError("Metadata manifest does not contain a parameters object.")

    normalized: dict[str, str] = {}
    for field in REQUIRED_FIELDS:
        value = str(parameters.get(field) or "").strip()
        if not value:
            raise ContractError(f"Metadata manifest is missing {field}.")
        if field in POSITIVE_ID_FIELDS and (not value.isdigit() or int(value) <= 0):
            raise ContractError(f"Metadata manifest field {field} must be a positive numeric ID.")
        normalized[field] = value
    for field in ("processName", "documentName"):
        if not VARIABLE_NAME.fullmatch(normalized[field]):
            raise ContractError(f"{field} must be an exact FACPQ variable name.")
    if not REST_VERSION.fullmatch(normalized["restFrameworkVersion"].lower()):
        raise ContractError("restFrameworkVersion must use v<number> syntax.")
    site = urllib.parse.urlsplit(normalized["faHostUrl"])
    if (
        site.scheme.lower() != "https"
        or not site.hostname
        or site.username
        or site.password
        or site.path not in {"", "/"}
        or site.query
        or site.fragment
    ):
        raise ContractError("faHostUrl must be one HTTPS Fusion host origin without credentials.")
    expected_endpoint = normalized["faHostUrl"].rstrip("/")
    if normalized["facpqEndpointUrl"].rstrip("/") != expected_endpoint:
        raise ContractError("facpqEndpointUrl must exactly equal faHostUrl and must not include /cpq.")
    return normalized


def action_urls(parameters: dict[str, str]) -> dict[str, str]:
    process = parameters["processName"]
    document_id = parameters["documentId"]
    copy_action_id = parameters["copyActionId"]
    version_action_id = parameters["versionActionId"]

    values = {
        "CreateQuoteUrl": (
            "#{'/cpq/sso/openid_connect_request.jsp?RelayState="
            "/fscmUI/redwood/cx-cpq/application/container/quotes/quotes-detail?"
            "create=true%26currency=USD%26mode=live"
            f"%26processVariableName={process}"
            "%26id=100106915720776%26inAppId=groupNode_RedwoodSales"
            "%26_partnerOpportunityNumber=' + (osc_param_OptyNumber ?: '')"
            " + '%26_partnerAccountId=' + (osc_param_AccountId ?: '')}"
        ),
        "EditQuoteUrl": (
            "#{'/cpq/sso/openid_connect_request.jsp?RelayState="
            "/fscmUI/redwood/cx-cpq/application/container/quotes/quotes-detail?"
            f"processVariableName={process}%26inAppId=groupNode_RedwoodSales%26id='"
            " + (osc_quote_ExternalReferenceNumber ?: '')}"
        ),
        "CopyQuoteUrl": (
            "#{'/sso/openid_connect_request.jsp?RelayState=/cpq/commerce/buyside/"
            "copy_processing.jsp?_partnerIdentifier=fusion"
            f"%26action_id={copy_action_id}%26version_id={version_action_id}%26bs_id='"
            + " + osc_quote_ExternalReferenceNumber"
            + f" + '%26document_id={document_id}'}}"
        ),
        "CreateVersionUrl": (
            "#{'/sso/openid_connect_request.jsp?RelayState=/cpq/commerce/buyside/"
            "document.jsp?_partnerIdentifier=fusion"
            + f"%26process={process}%26formaction=version%26action_id={version_action_id}%26bs_id='"
            + " + osc_quote_ExternalReferenceNumber}"
        ),
        "GetProposalUrl": (
            "#{'/sso/openid_connect_request.jsp?RelayState=/cpq/rest/v10/"
            f"commerceProcesses/{process}/transactions/'"
            + " +osc_quote_ExternalReferenceNumber+ '/attachments/oRCL_OSC_FileAttachment_t'}"
        ),
    }
    if any(value != value.strip() for value in values.values()):
        raise ContractError("Constructed action URL values must not contain outer whitespace.")
    return values


def resolve(manifest_path: str) -> dict[str, Any]:
    parameters = load_ready_manifest(manifest_path)
    return {
        "schema_version": "2.0",
        "status": "ready",
        "operation": "resolve_cpq_action_url_contract",
        "platform": "FACPQ",
        "sso_family": "oidc",
        "action_urls": action_urls(parameters),
        "source_manifest": str(Path(manifest_path).expanduser().resolve()),
        "boundaries": {
            "network_requests": False,
            "facpq_mutations": False,
            "bm_cpq_supported": False,
            "fusion_mutations": False,
        },
    }
