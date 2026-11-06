#!/usr/bin/env python3
"""Unified CLI for the FACPQ Sales integration workflow.

Subcommands preserve the former runtime entry points:
metadata, action-urls, and build-package.
"""

from __future__ import annotations

import sys
import types

FACPQ_METADATA_GET_SOURCE = "#!/usr/bin/env python3\n\"\"\"GET-only HTTP helper for this task's Fusion Application CPQ metadata.\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport os\nimport re\nimport urllib.parse\nimport urllib.request\nfrom typing import Any\n\n\nVARIABLE_NAME = r\"[A-Za-z_][A-Za-z0-9_]*\"\nMETADATA_PATH = re.compile(\n    rf\"^/cpq/rest/v[0-9]+/commerceProcesses/{VARIABLE_NAME}/documents\"\n    rf\"(?:/{VARIABLE_NAME}/actionDefs)?$\"\n)\nREDACTED_KEY = re.compile(\n    r\"password|token|secret|authorization|credential\", re.IGNORECASE\n)\nSAFE_RESPONSE_HEADERS = {\n    \"content-type\",\n    \"x-request-id\",\n    \"x-oracle-dms-ecid\",\n}\n\n\nclass ClientError(ValueError):\n    \"\"\"Input, safety, or response-contract failure.\"\"\"\n\n\ndef redact(value: Any) -> Any:\n    \"\"\"Redact secret-like response fields before output or persistence.\"\"\"\n    if isinstance(value, dict):\n        return {\n            key: \"[REDACTED]\" if REDACTED_KEY.search(str(key)) else redact(item)\n            for key, item in value.items()\n        }\n    if isinstance(value, list):\n        return [redact(item) for item in value]\n    return value\n\n\ndef validate_fa_host_url(value: str) -> str:\n    parsed = urllib.parse.urlsplit(value.strip())\n    if parsed.scheme.lower() != \"https\":\n        raise ClientError(\"Fusion Application host URL must use HTTPS.\")\n    if not parsed.hostname or parsed.username or parsed.password:\n        raise ClientError(\"Fusion Application host URL must contain a host and no credentials.\")\n    if parsed.path not in {\"\", \"/\"} or parsed.query or parsed.fragment:\n        raise ClientError(\n            \"Fusion Application host URL must be the site origin without /cpq, \"\n            \"another path, a query, or a fragment.\"\n        )\n    port = f\":{parsed.port}\" if parsed.port else \"\"\n    return f\"https://{parsed.hostname}{port}\"\n\n\ndef validate_endpoint(value: str) -> str:\n    endpoint = value.strip()\n    if not METADATA_PATH.fullmatch(endpoint):\n        raise ClientError(\n            \"Only the documented documents and document actionDefs collection paths are allowed.\"\n        )\n    return endpoint\n\n\ndef authorization_header(\n    auth_mode: str,\n    token_env: str,\n    access_token: str | None = None,\n) -> str | None:\n    if auth_mode == \"none\":\n        return None\n    if auth_mode == \"bearer\":\n        token = access_token or os.environ.get(token_env)\n        if not token:\n            raise ClientError(f\"Bearer authentication requires runtime variable {token_env}.\")\n        return f\"Bearer {token}\"\n    raise ClientError(f\"Unsupported authentication mode: {auth_mode}.\")\n\n\ndef get_json(\n    *,\n    fa_host_url: str,\n    endpoint: str,\n    auth_mode: str,\n    token_env: str,\n    timeout: float,\n    access_token: str | None = None,\n) -> dict[str, Any]:\n    \"\"\"Execute one guarded metadata GET and return a sanitized JSON object.\"\"\"\n    origin = validate_fa_host_url(fa_host_url)\n    path = validate_endpoint(endpoint)\n    if timeout <= 0:\n        raise ClientError(\"Timeout must be greater than zero seconds.\")\n\n    headers = {\n        \"Accept\": \"application/json\",\n        \"User-Agent\": \"FDOS-CX-Sales-FACPQ-Metadata/0.3\",\n    }\n    authorization = authorization_header(auth_mode, token_env, access_token)\n    if authorization:\n        headers[\"Authorization\"] = authorization\n\n    request = urllib.request.Request(\n        url=f\"{origin}{path}\", headers=headers, method=\"GET\"\n    )\n    with FUSION_AUTH.authorized_urlopen(getattr(access_token, \"context\", {\"restBaseUrl\": origin}), request, timeout=timeout, access_token=access_token) as response:\n        content = response.read()\n        try:\n            body = json.loads(content.decode(\"utf-8\"))\n        except (UnicodeDecodeError, json.JSONDecodeError) as exc:\n            raise ClientError(\"CPQ metadata response is not valid JSON.\") from exc\n        if not isinstance(body, dict):\n            raise ClientError(\"CPQ metadata response must be a JSON object.\")\n        return {\n            \"body\": redact(body),\n            \"http_status\": response.status,\n            \"response_headers\": {\n                key: value\n                for key, value in response.headers.items()\n                if key.lower() in SAFE_RESPONSE_HEADERS\n            },\n        }\n"

import argparse
import importlib.util
import json
import os
import re
import socket
import tempfile
import sys
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
PROJECTS_ROOT = REPOSITORY_ROOT / "project"
DEFAULT_PROPERTIES_PATH = REPOSITORY_ROOT / "core/auth/fusionEnv.properties"
DEFAULT_TOKEN_CACHE = Path("auto")

AUTH_PATH = (
    REPOSITORY_ROOT
    / "core/auth/fusion-oauth-authentication/scripts/fusion_auth.py"
)
AUTH_SPEC = importlib.util.spec_from_file_location("fdos_fusion_auth_cpq", AUTH_PATH)
assert AUTH_SPEC and AUTH_SPEC.loader
FUSION_AUTH = importlib.util.module_from_spec(AUTH_SPEC)
AUTH_SPEC.loader.exec_module(FUSION_AUTH)

CPQ_GET = types.ModuleType("facpq_metadata_get")
CPQ_GET.__file__ = __file__
CPQ_GET.FUSION_AUTH = FUSION_AUTH
exec(FACPQ_METADATA_GET_SOURCE, CPQ_GET.__dict__)

VARIABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
REST_VERSION = re.compile(r"^v[0-9]+$")
POSITIVE_ID = re.compile(r"^[1-9][0-9]*$")
PLACEHOLDER_HOSTS = {"thisurlmustbechanged.com"}
VIEW_PARAMETER_KEYS = {
    "process_id": "commerceProcessId",
    "action_id_copy": "copyActionId",
    "action_id_version": "versionActionId",
    "document_id": "documentId",
    "process": "processName",
    "url": "faHostUrl",
}
ID_FIELDS = {
    "commerceProcessId",
    "documentId",
    "copyActionId",
    "versionActionId",
}
REQUIRED_FIELDS = [
    "faHostUrl",
    "facpqEndpointUrl",
    "restFrameworkVersion",
    "processName",
    "documentName",
    "documentId",
    "copyActionId",
    "versionActionId",
]
OUTPUT_FIELDS = [*REQUIRED_FIELDS, "commerceProcessId"]
ACTION_ROLES = {
    "copyActionId": "copy",
    "versionActionId": "version",
}


class ResolverError(ValueError):
    """Input or read-only safety validation failure."""


class MetadataMismatch(ResolverError):
    """Conflicting values were returned by two read-only sources."""


class OAuthAuthenticationError(RuntimeError):
    """Fresh Fusion OAuth login failed without exposing provider details."""


def validate_variable_name(value: str, label: str) -> str:
    candidate = value.strip()
    if not VARIABLE_NAME.fullmatch(candidate):
        raise ResolverError(
            f"{label} must be an exact CPQ variable name containing only letters, digits, and underscores."
        )
    return candidate


def validate_rest_version(value: str) -> str:
    candidate = value.strip().lower()
    if not REST_VERSION.fullmatch(candidate):
        raise ResolverError("REST version must use v<number> syntax, for example v19.")
    return candidate


def normalize_id(value: Any, field: str) -> str:
    candidate = str(value).strip()
    if not POSITIVE_ID.fullmatch(candidate):
        raise ResolverError(f"{field} must be a positive numeric Oracle CPQ identifier.")
    return candidate


def origin_from_url(value: str, label: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ResolverError(f"{label} must be an HTTPS Fusion Application URL.")
    if parsed.username or parsed.password:
        raise ResolverError(f"{label} must not contain embedded credentials.")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ResolverError(
            f"{label} must contain only the Fusion host origin without /cpq, "
            "another path, a query, or a fragment."
        )
    if parsed.hostname.lower() in PLACEHOLDER_HOSTS:
        raise ResolverError(
            f"{label} must use the selected Fusion environment, not a placeholder host."
        )
    port = f":{parsed.port}" if parsed.port else ""
    return f"https://{parsed.hostname}{port}"


def facpq_endpoint_from_host(value: str) -> str:
    """Return the Sales integration endpoint as the Fusion host origin only."""
    return origin_from_url(value, "Fusion Application host URL")


def validate_token_cache_path(value: str) -> str:
    """Use the managed profile cache or a validated external private path."""
    if value == "auto":
        return value
    try:
        return str(FUSION_AUTH.validate_cache_path(Path(value)))
    except ValueError as exc:
        raise ResolverError(str(exc)) from exc


def get_fresh_fusion_access_token(
    args: argparse.Namespace, fa_host_url: str
) -> str:
    """Login once using the dedicated cpq_scope property and return the token."""
    properties_path = Path(args.properties).expanduser().resolve()
    try:
        props = dict(FUSION_AUTH.read_properties(properties_path))
    except (OSError, ValueError) as exc:
        raise ResolverError(
            "The selected Fusion OAuth properties file could not be read or has "
            "invalid syntax; property values were suppressed."
        ) from exc

    configured_cpq_scope = props.get("cpq_scope", "").strip()
    if not configured_cpq_scope:
        raise ResolverError(
            "The selected Fusion OAuth properties file must define a non-empty "
            "cpq_scope property; scope is not used as a fallback."
        )
    configured_host = props.get("restBaseUrl", "").strip()
    if not configured_host:
        raise ResolverError(
            "The selected Fusion OAuth properties file must define restBaseUrl."
        )
    try:
        configured_origin = CPQ_GET.validate_fa_host_url(configured_host)
    except CPQ_GET.ClientError as exc:
        raise ResolverError(
            "The selected Fusion OAuth properties file has an invalid restBaseUrl."
        ) from exc
    if configured_origin != fa_host_url:
        raise ResolverError(
            "The selected Fusion OAuth properties file identifies a different "
            "Fusion host than --fa-host-url."
        )

    # The shared OAuth helper consumes `scope`. Map the dedicated `cpq_scope`
    # value in this in-memory copy without changing the properties file.
    props["scope"] = configured_cpq_scope
    token_cache = validate_token_cache_path(args.token_cache)
    try:
        return FUSION_AUTH.get_access_token(
            props,
            redirect_url=args.redirect_url,
            auth_code=args.auth_code,
            code_verifier=args.code_verifier,
            open_browser=args.open_browser,
            callback_timeout=args.callback_timeout,
            token_cache=token_cache,
            force_login=True,
        )
    except Exception as exc:
        raise OAuthAuthenticationError(
            "Fresh Fusion OAuth login using cpq_scope "
            "failed; provider details and token values were suppressed."
        ) from exc


def parse_view_parameters(path_value: str) -> dict[str, str]:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise ResolverError(f"View Parameters evidence does not exist: {path}")
    content = path.read_text(encoding="utf-8", errors="replace")
    resolved: dict[str, str] = {}
    for source_key, field in VIEW_PARAMETER_KEYS.items():
        pattern = re.compile(
            rf"(?im)(?<![A-Za-z0-9_]){re.escape(source_key)}(?![A-Za-z0-9_])"
            r"\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s;]+))"
        )
        matches = {
            next(group for group in match.groups() if group is not None).strip()
            for match in pattern.finditer(content)
        }
        matches.discard("")
        if len(matches) > 1:
            raise MetadataMismatch(
                f"View Parameters evidence contains multiple values for {source_key}."
            )
        if matches:
            resolved[field] = matches.pop()
    return resolved


def normalize_field(field: str, value: Any) -> str:
    if field in ID_FIELDS:
        return normalize_id(value, field)
    if field in {"processName", "documentName"}:
        return validate_variable_name(str(value), field)
    if field == "restFrameworkVersion":
        return validate_rest_version(str(value))
    if field == "faHostUrl":
        return origin_from_url(str(value), "Fusion Application host URL")
    if field == "facpqEndpointUrl":
        candidate = str(value).strip().rstrip("/")
        host = origin_from_url(candidate, "Sales integration endpoint URL")
        if candidate != host:
            raise ResolverError(
                "facpqEndpointUrl must contain only the Fusion host URL and must not include /cpq."
            )
        return candidate
    return str(value).strip()


def merge_value(
    values: dict[str, str],
    sources: dict[str, list[str]],
    field: str,
    raw_value: Any | None,
    source: str,
) -> None:
    if raw_value is None or str(raw_value).strip() == "":
        return
    value = normalize_field(field, raw_value)
    if field in values and values[field] != value:
        raise MetadataMismatch(
            f"Conflicting {field}: {values[field]!r} from {sources[field]} versus {value!r} from {source}."
        )
    values[field] = value
    if source not in sources.setdefault(field, []):
        sources[field].append(source)


def metadata_requests(args: argparse.Namespace) -> list[dict[str, str]]:
    process = validate_variable_name(args.process_var_name, "processVarName")
    version = validate_rest_version(args.rest_version)
    for label, selector in (
        ("copyActionVarName", args.copy_action_var_name),
        ("versionActionVarName", args.version_action_var_name),
    ):
        if selector:
            validate_variable_name(selector, label)
    document = (
        validate_variable_name(args.document_var_name, "documentVarName")
        if args.document_var_name
        else "{resolvedMainDocumentVarName}"
    )
    prefix = f"/cpq/rest/{version}/commerceProcesses/{process}/documents"
    return [
        {"kind": "documents", "method": "GET", "endpoint": prefix},
        {
            "kind": "actions",
            "method": "GET",
            "endpoint": f"{prefix}/{document}/actionDefs",
        },
    ]


def run_metadata_get(
    args: argparse.Namespace,
    endpoint: str,
    access_token: str,
    auth_mode: str,
) -> dict[str, Any]:
    return CPQ_GET.get_json(
        fa_host_url=args.fa_host_url,
        endpoint=endpoint,
        auth_mode=auth_mode,
        token_env="FDOS_EXPLICIT_ACCESS_TOKEN_ONLY",
        timeout=args.timeout,
        access_token=access_token,
    )


def collection_items(body: dict[str, Any], endpoint: str) -> list[dict[str, Any]]:
    items = body.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise MetadataMismatch(f"CPQ metadata response for {endpoint} does not contain an items collection.")
    return items


def summarize_document(item: dict[str, Any]) -> dict[str, Any]:
    process = item.get("process") if isinstance(item.get("process"), dict) else {}
    document_type = item.get("type") if isinstance(item.get("type"), dict) else {}
    return {
        "id": item.get("id"),
        "variableName": item.get("variableName"),
        "label": item.get("label"),
        "type": document_type.get("displayValue"),
        "processId": process.get("id"),
        "processVarName": process.get("variableName"),
    }


def select_document(
    items: list[dict[str, Any]], selector: str | None
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if selector:
        exact = [item for item in items if item.get("variableName") == selector]
        return (exact[0] if len(exact) == 1 else None, [summarize_document(item) for item in exact or items])
    main = []
    for item in items:
        document_type = item.get("type") if isinstance(item.get("type"), dict) else {}
        if str(document_type.get("lookupCode")) == "0" or str(document_type.get("displayValue", "")).lower() == "main document":
            main.append(item)
    return (main[0] if len(main) == 1 else None, [summarize_document(item) for item in main or items])


def summarize_action(item: dict[str, Any]) -> dict[str, Any]:
    action_type = item.get("type") if isinstance(item.get("type"), dict) else {}
    return {
        "id": item.get("id"),
        "variableName": item.get("variableName"),
        "label": item.get("label"),
        "type": action_type.get("displayValue"),
        "isAvailable": item.get("isAvailable"),
    }


def action_matches_role(item: dict[str, Any], role: str) -> bool:
    """Return whether an available action matches the requested Sales URL role."""
    if item.get("isAvailable") is False:
        return False
    action_type = item.get("type") if isinstance(item.get("type"), dict) else {}
    label = str(item.get("label", "")).strip().lower()
    variable = str(item.get("variableName", "")).strip().lower()
    type_name = str(action_type.get("displayValue", "")).strip().lower()
    has_line_scope = "line" in label or "line" in variable
    if role == "copy":
        return (
            label in {"copy", "copy quote", "copy transaction"}
            or variable == "_action_process_resubmit"
            or (type_name == "copy" and not has_line_scope)
        )
    if role == "version":
        return (
            label in {"version transaction", "create version", "create a version"}
            or variable == "versiontransaction_t"
            or type_name == "version"
        )
    raise ResolverError(f"Unsupported action role: {role}.")


def action_role_candidates(items: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    return [item for item in items if action_matches_role(item, role)]


def select_action(
    items: list[dict[str, Any]], role: str, selector: str | None
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if selector:
        selector = validate_variable_name(selector, f"{role}ActionVarName")
        exact = [item for item in items if item.get("variableName") == selector]
        if len(exact) == 1 and not action_matches_role(exact[0], role):
            raise MetadataMismatch(
                f"Action selector {selector!r} does not identify an available {role} action."
            )
        return (
            exact[0] if len(exact) == 1 else None,
            [summarize_action(item) for item in exact or action_role_candidates(items, role)],
        )
    candidates = action_role_candidates(items, role)
    return (
        candidates[0] if len(candidates) == 1 else None,
        [summarize_action(item) for item in candidates],
    )


def required_input(field: str, option: str, prompt: str, candidates: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"field": field, "cli_option": option, "prompt": prompt}
    if candidates:
        result["candidates"] = candidates
    return result


def resolve(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    fa_host_url = CPQ_GET.validate_fa_host_url(args.fa_host_url)
    values: dict[str, str] = {}
    sources: dict[str, list[str]] = {}
    merge_value(values, sources, "faHostUrl", fa_host_url, "cli:fa-host-url")
    merge_value(
        values,
        sources,
        "facpqEndpointUrl",
        facpq_endpoint_from_host(fa_host_url),
        "derived:fa-host-url",
    )
    merge_value(values, sources, "restFrameworkVersion", args.rest_version, "cli:rest-version")
    merge_value(values, sources, "processName", args.process_var_name, "cli:process-var-name")
    merge_value(values, sources, "documentName", args.document_var_name, "cli:document-var-name")

    explicit = {
        "commerceProcessId": args.commerce_process_id,
        "documentId": args.document_id,
        "copyActionId": args.copy_action_id,
        "versionActionId": args.version_action_id,
    }
    for field, value in explicit.items():
        merge_value(values, sources, field, value, f"cli:{field}")

    if args.view_parameters_file:
        for field, value in parse_view_parameters(args.view_parameters_file).items():
            merge_value(values, sources, field, value, "cpq:view-parameters")
    request_plan = metadata_requests(args)
    requests: list[dict[str, Any]] = [dict(item, status="planned") for item in request_plan]
    required_user_inputs: list[dict[str, Any]] = []
    discovery: dict[str, Any] = {}

    if args.execute:
        if args.auth_mode != "oauth":
            raise ResolverError(
                "Live FACPQ metadata discovery requires a fresh Fusion OAuth login "
                "using the cpq_scope property."
            )
        fusion_access_token = get_fresh_fusion_access_token(args, fa_host_url)
        documents_endpoint = request_plan[0]["endpoint"]
        documents_result = run_metadata_get(
            args,
            documents_endpoint,
            fusion_access_token,
            "bearer",
        )
        requests[0].update(
            status="success",
            http_status=documents_result["http_status"],
            authentication="fusion_oauth_bearer",
        )
        discovery["authentication"] = {
            "route": "fusion_oauth_direct",
            "fresh_login": True,
            "cpq_scope_metadata_access_verified": True,
            "oauth_scope_property": "cpq_scope",
            "oauth_scope_selection": "dedicated_property",
            "fusion_oauth_cache_policy": "managed_private_cache_outside_repository",
        }

        documents = collection_items(documents_result["body"], documents_endpoint)
        document, document_candidates = select_document(documents, args.document_var_name)
        discovery["document_candidates"] = document_candidates

        if document is None:
            required_user_inputs.append(required_input(
                "documentName",
                "--document-var-name",
                "Provide the exact main-document variable name returned by the documents GET.",
                document_candidates,
            ))
            requests[1]["status"] = "blocked_pending_document_selector"
        else:
            document_name = document.get("variableName")
            merge_value(values, sources, "documentName", document_name, f"cpq-rest:GET {documents_endpoint}")
            if "id" not in document:
                raise MetadataMismatch("Selected CPQ document metadata does not contain id.")
            merge_value(values, sources, "documentId", document["id"], f"cpq-rest:GET {documents_endpoint}")
            process = document.get("process")
            if not isinstance(process, dict) or "id" not in process:
                raise MetadataMismatch("Selected CPQ document metadata does not contain process.id.")
            if process.get("variableName") and process.get("variableName") != args.process_var_name:
                raise MetadataMismatch("Selected CPQ document belongs to a different commerce process.")
            merge_value(values, sources, "commerceProcessId", process["id"], f"cpq-rest:GET {documents_endpoint}")

            actions_endpoint = (
                f"/cpq/rest/{validate_rest_version(args.rest_version)}/commerceProcesses/"
                f"{validate_variable_name(args.process_var_name, 'processVarName')}/documents/"
                f"{validate_variable_name(str(document_name), 'documentVarName')}/actionDefs"
            )
            requests[1]["endpoint"] = actions_endpoint
            actions_result = run_metadata_get(
                args,
                actions_endpoint,
                fusion_access_token,
                "bearer",
            )
            actions = collection_items(actions_result["body"], actions_endpoint)
            requests[1].update(
                status="success",
                http_status=actions_result["http_status"],
                authentication="fusion_oauth_bearer",
            )
            selectors = {
                "copyActionId": args.copy_action_var_name,
                "versionActionId": args.version_action_var_name,
            }
            discovery["action_candidates"] = {}
            for field, role in ACTION_ROLES.items():
                if not selectors[field] and field in values:
                    action_id = values[field]
                    id_matches = [
                        item for item in actions if str(item.get("id", "")).strip() == action_id
                    ]
                    if len(id_matches) != 1:
                        raise MetadataMismatch(
                            f"The supplied {field} {action_id!r} does not identify exactly one "
                            "action returned by the actionDefs GET."
                        )
                    action = id_matches[0]
                    if not action_matches_role(action, role):
                        raise MetadataMismatch(
                            f"The supplied {field} {action_id!r} does not identify an "
                            f"available {role} action."
                        )
                    candidates = [summarize_action(action)]
                else:
                    action, candidates = select_action(actions, role, selectors[field])
                discovery["action_candidates"][role] = candidates
                if action is None:
                    required_user_inputs.append(required_input(
                        field,
                        f"--{role}-action-var-name",
                        f"Select the exact {role} action variable name returned by the actionDefs GET.",
                        candidates,
                    ))
                    continue
                if "id" not in action:
                    raise MetadataMismatch(f"Selected {role} action metadata does not contain id.")
                merge_value(values, sources, field, action["id"], f"cpq-rest:GET {actions_endpoint}")

    missing = [field for field in REQUIRED_FIELDS if field not in values]
    complete = not missing
    status = "preview" if not args.execute else ("ready" if complete else "missing")
    payload = {
        "schema_version": "1.0",
        "status": status,
        "completeness": "complete" if complete else "incomplete",
        "operation": "resolve_fusion_application_cpq_metadata",
        "parameters": {field: values.get(field) for field in OUTPUT_FIELDS},
        "metadata_selectors": {
            "processVarName": args.process_var_name,
            "documentVarName": args.document_var_name,
            "copyActionVarName": args.copy_action_var_name,
            "versionActionVarName": args.version_action_var_name,
        },
        "sources": {field: sources[field] for field in OUTPUT_FIELDS if field in sources},
        "missing_fields": missing,
        "required_user_inputs": required_user_inputs,
        "discovery": discovery,
        "requests": requests,
        "boundaries": {
            "allowed_facpq_methods": ["GET"],
            "facpq_mutations": False,
            "bm_cpq_supported": False,
            "authentication_chain": "idcs_cpq_scope_fusion_oauth_direct",
            "idcs_cpq_scope_assignment_required": True,
            "oauth_scope_property": "cpq_scope",
            "oauth_scope_selection": "dedicated_property",
            "fresh_oauth_login": True,
            "fusion_oauth_cache_policy": "managed_private_cache_outside_repository",
            "consumer": "cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration",
        },
    }
    return payload, 0 if not args.execute or complete else 2


def validate_output_path(path_value: str, overwrite: bool) -> Path:
    """Preflight a local artifact without following symbolic links."""
    path = Path(path_value).expanduser()
    if ".." in path.parts:
        raise ResolverError("Output must not contain parent-directory traversal.")
    path = path.absolute()
    projects_root = PROJECTS_ROOT.resolve()
    try:
        relative = path.relative_to(projects_root)
    except ValueError as exc:
        raise ResolverError(
            "Output must be inside an existing project/{project_id} workspace."
        ) from exc
    if (
        len(relative.parts) < 3
        or relative.parts[0] == "_template"
        or relative.parts[1] not in {"artifacts", "exports", "baselines", "decisions", "blueprints"}
    ):
        raise ResolverError(
            "Output must name an artifact inside a non-template project/{project_id} workspace."
        )
    current = projects_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ResolverError("Output must not use symbolic links.")
    project_root = projects_root / relative.parts[0]
    state_path = project_root / "state" / "project-state.json"
    if (project_root / "state").is_symlink() or state_path.is_symlink():
        raise ResolverError("Project initialization evidence must not use symbolic links.")
    if not state_path.is_file():
        raise ResolverError(
            "Project workspace is not initialized; initialize it before persisting output."
        )
    if path.exists() and not overwrite:
        raise ResolverError("Output already exists; use --overwrite-output only after explicit approval.")
    if path.exists() and not path.is_file():
        raise ResolverError("Output must be a file path, not an existing directory.")
    return path


def persist_output(payload: dict[str, Any], path_value: str, overwrite: bool) -> None:
    path = validate_output_path(path_value, overwrite)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".facpq-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        validate_output_path(path_value, overwrite)
        if overwrite:
            os.replace(temporary, path)
        else:
            # Publish without replacing a file created after preflight.
            os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--fa-host-url",
        "--base-url",
        dest="fa_host_url",
        required=True,
        help="HTTPS Fusion Application host origin; do not append /cpq.",
    )
    result.add_argument("--rest-version", default="v19")
    result.add_argument("--process-var-name", required=True)
    result.add_argument("--document-var-name", help="Optional exact main-document variable name; otherwise discover it from the documents GET.")
    result.add_argument("--copy-action-var-name")
    result.add_argument("--version-action-var-name")
    result.add_argument("--view-parameters-file")
    result.add_argument("--commerce-process-id")
    result.add_argument("--document-id")
    result.add_argument("--copy-action-id")
    result.add_argument("--version-action-id")
    result.add_argument(
        "--auth-mode",
        choices=["oauth", "none"],
        default="oauth",
    )
    result.add_argument(
        "--properties",
        default=str(DEFAULT_PROPERTIES_PATH),
        help=(
            "Fusion OAuth properties file containing restBaseUrl and a non-empty "
            "cpq_scope property used directly for metadata authentication."
        ),
    )
    result.add_argument(
        "--token-cache",
        default=str(DEFAULT_TOKEN_CACHE),
        help="Managed private Fusion OAuth cache outside the repository; auto selects the authentication service default.",
    )
    result.add_argument("--auth-code", help="Optional OAuth authorization code for the fresh login.")
    result.add_argument("--code-verifier", help="Required with --auth-code when pkce=true.")
    result.add_argument("--redirect-url", help="Optional OAuth redirect URI override.")
    result.add_argument(
        "--callback-timeout",
        type=int,
        default=FUSION_AUTH.DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    )
    result.add_argument("--open-browser", action="store_true", default=True)
    result.add_argument("--no-open-browser", action="store_false", dest="open_browser")
    result.add_argument("--timeout", type=float, default=60.0)
    result.add_argument("--execute", action="store_true")
    result.add_argument("--output")
    result.add_argument("--overwrite-output", action="store_true")
    return result


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(CPQ_GET.redact(payload), indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.timeout <= 0 or args.callback_timeout <= 0:
            raise ResolverError("Timeout values must be greater than zero.")
        validate_token_cache_path(args.token_cache)
        if args.output:
            validate_output_path(args.output, args.overwrite_output)
        if args.execute and args.auth_mode == "none":
            raise ResolverError(
                "Live FACPQ metadata discovery requires a fresh Fusion OAuth login "
                "using the cpq_scope property."
            )
        payload, exit_code = resolve(args)
        if args.output:
            persist_output(payload, args.output, args.overwrite_output)
            payload["output"] = str(Path(args.output).expanduser().resolve())
        emit(payload)
        return exit_code
    except MetadataMismatch as exc:
        emit({
            "status": "failed",
            "failure_class": "catalog_or_metadata_mismatch",
            "message": str(exc),
            "recommended_action": "Recollect all values from exactly one Fusion host and FACPQ process.",
        })
        return 2
    except (ResolverError, CPQ_GET.ClientError) as exc:
        emit({"status": "failed", "failure_class": "input_validation", "message": str(exc)})
        return 1
    except OAuthAuthenticationError as exc:
        emit({
            "status": "failed",
            "failure_class": "authorization_or_privilege",
            "failed_stage": "fresh_fusion_oauth_login",
            "message": str(exc),
            "recommended_action": (
                "Verify the target-host OAuth properties and cpq_scope, then start one new login."
            ),
        })
        return 4
    except urllib.error.HTTPError as exc:
        failure_class = "authorization_or_privilege" if exc.code in {401, 403} else "fusion_api_error"
        emit({
            "status": "failed",
            "failure_class": failure_class,
            "http_status": exc.code,
            "message": "Fusion Application CPQ rejected a read-only metadata request.",
            "recommended_action": "Verify that cpq_scope is assigned to the target IDCS OAuth client and authorized for FACPQ metadata reads."
            if exc.code in {401, 403}
            else "Review the /cpq/rest metadata endpoint and Fusion response before retrying.",
        })
        return 4 if exc.code in {401, 403} else 2
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        emit({
            "status": "failed",
            "failure_class": "transport_or_environment",
            "message": str(exc.reason if isinstance(exc, urllib.error.URLError) else exc),
            "recommended_action": "Verify the Fusion host, /cpq route, network path, TLS trust, and timeout before retrying the read.",
        })
        return 3



METADATA_MAIN = main

_ACTION_SPEC = importlib.util.spec_from_file_location(
    "facpq_action_urls", Path(__file__).with_name("facpq_action_urls.py")
)
assert _ACTION_SPEC and _ACTION_SPEC.loader
_ACTION_MODULE = importlib.util.module_from_spec(_ACTION_SPEC)
_ACTION_SPEC.loader.exec_module(_ACTION_MODULE)
_ACTION_NAMESPACE = vars(_ACTION_MODULE)

def _load_action_manifest_with_host_endpoint(path_value: str) -> dict[str, str]:
    """Load an action manifest whose integration endpoint is the Fusion origin."""
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise _ACTION_NAMESPACE["ContractError"](
            f"Metadata manifest does not exist: {path}"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise _ACTION_NAMESPACE["ContractError"](
            "Metadata manifest must be a readable JSON object."
        ) from exc
    if not isinstance(payload, dict):
        raise _ACTION_NAMESPACE["ContractError"](
            "Metadata manifest must be a JSON object."
        )
    if payload.get("status") != "ready" or payload.get("completeness") != "complete":
        raise _ACTION_NAMESPACE["ContractError"](
            "Metadata manifest must have status ready and completeness complete."
        )
    boundaries = payload.get("boundaries")
    if (
        not isinstance(boundaries, dict)
        or boundaries.get("facpq_mutations") is not False
        or boundaries.get("allowed_facpq_methods") != ["GET"]
        or boundaries.get("bm_cpq_supported") is not False
        or boundaries.get("consumer")
        != "cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration"
    ):
        raise _ACTION_NAMESPACE["ContractError"](
            "Metadata manifest must declare a GET-only FACPQ boundary with BM CPQ disabled."
        )
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise _ACTION_NAMESPACE["ContractError"](
            "Metadata manifest does not contain a parameters object."
        )
    missing = [
        field
        for field in REQUIRED_FIELDS
        if parameters.get(field) is None or not str(parameters.get(field)).strip()
    ]
    if missing:
        raise _ACTION_NAMESPACE["ContractError"](
            "Metadata manifest is missing " + ", ".join(missing) + "."
        )
    try:
        normalized = {
            field: normalize_field(field, parameters.get(field))
            for field in REQUIRED_FIELDS
        }
    except ResolverError as exc:
        raise _ACTION_NAMESPACE["ContractError"](str(exc)) from exc
    if normalized["facpqEndpointUrl"] != normalized["faHostUrl"]:
        raise _ACTION_NAMESPACE["ContractError"](
            "facpqEndpointUrl must exactly equal faHostUrl and must not include /cpq."
        )
    return normalized


# The action URL module retains the fixed action URL expressions. Replace
# only its manifest loader so the Sales integration endpoint follows the current
# host-only contract.
_ACTION_NAMESPACE["load_ready_manifest"] = _load_action_manifest_with_host_endpoint

def run_action_urls(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Construct the five FACPQ action URLs without network requests.")
    parser.add_argument("--manifest", required=True, help="Ready metadata manifest JSON.")
    parser.add_argument("--output", help="Optional JSON artifact in the manifest's initialized repository project.")
    parser.add_argument("--overwrite-output", action="store_true", help="Replace the named artifact only after explicit overwrite approval.")
    args = parser.parse_args(arguments)
    if args.overwrite_output and not args.output:
        parser.error("--overwrite-output requires --output")
    try:
        if args.output:
            output = validate_output_path(args.output, args.overwrite_output)
            relative = output.relative_to(PROJECTS_ROOT.resolve())
            project_root = PROJECTS_ROOT.resolve() / relative.parts[0]
            if not Path(args.manifest).expanduser().resolve().is_relative_to(project_root):
                raise ResolverError("Manifest and output must belong to the same initialized project.")
        payload = _ACTION_NAMESPACE["resolve"](args.manifest)
        if args.output:
            persist_output(payload, args.output, args.overwrite_output)
            payload["output"] = str(output)
        emit(payload)
        return 0
    except (ResolverError, _ACTION_NAMESPACE["ContractError"]) as exc:
        emit({"status": "failed", "failure_class": "input_validation", "message": str(exc)})
        return 1
    except OSError:
        emit({"status": "failed", "failure_class": "artifact_persistence", "message": "Could not read or publish the requested action-URL artifact; no overwrite was authorized implicitly."})
        return 1


def unified_parser() -> "argparse.ArgumentParser":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("metadata", "action-urls", "build-package"),
        help="metadata resolves FACPQ values; action-urls builds the five URLs; build-package creates the FSM ZIP.",
    )
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    return parser


def unified_main(argv: list[str] | None = None) -> int:
    parsed = unified_parser().parse_args(argv)
    if parsed.command == "metadata":
        return METADATA_MAIN(parsed.arguments)
    if parsed.command == "action-urls":
        return run_action_urls(parsed.arguments)
    from facpq_package_builder import main as build_package

    original_argv = sys.argv
    try:
        sys.argv = [f"{original_argv[0]} build-package", *parsed.arguments]
        return build_package()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(unified_main())
