#!/usr/bin/env python3
"""Run the EPM Data Integrator format, preview, and approval-bound POST flow."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlencode, urlsplit, urlunsplit

from openapi_output_formatter import convert_to_extraction_objects

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from openapi_response_schema_validator import validate_openapi_response_schemas
from connector_artifacts import (
    artifact_path, new_preview_directory, publish_current_pointer, write_new_text,
)


POST_PATH = "/api/risk-cloud/rc-tools-ms/dataintegration/v1/dataIntegratorConnectorDefinitions"
PROHIBITED_FIELDS = {
    "authenticationDetails", "clientSecret", "accessToken", "refreshToken", "privateKey",
}
BASE_CONNECTOR_SETUP_KEYS = {
    "authType",
    "grantType",
    "hostUrl",
    "accessTokenUrl",
    "scopes",
    "assertionUserName",
    "assertionKeyAlias",
    "assertionAudienceList",
}
REVIEW_ARTIFACT_DIRECTORY = Path("artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-epm-data-sources/current")
SOURCE_TYPE_REGISTRY = Path(__file__).resolve().parents[2] / "connector-source-types.json"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def resolve_source_type(connector_type: str) -> dict[str, Any]:
    registry = json.loads(SOURCE_TYPE_REGISTRY.read_text(encoding="utf-8"))
    source_types = registry.get("sourceTypes") if isinstance(registry, dict) else None
    source_type = source_types.get(connector_type) if isinstance(source_types, dict) else None
    if (
        not isinstance(source_type, dict)
        or not isinstance(source_type.get("sourceTypeName"), str)
        or isinstance(source_type.get("sourceTypeCode"), bool)
        or not isinstance(source_type.get("sourceTypeCode"), int)
    ):
        raise ValueError(f"No valid central source-type definition exists for {connector_type!r}")
    return source_type


def reject_prohibited(value: Any) -> None:
    """Reject prohibited connector-definition fields recursively."""
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in PROHIBITED_FIELDS:
                raise ValueError(f"payload contains a prohibited field: {key}")
            reject_prohibited(nested)
    elif isinstance(value, list):
        for nested in value:
            reject_prohibited(nested)


def normalize_target(value: str) -> str:
    parsed = urlsplit(value.strip())
    if (parsed.scheme.lower() != "https" or not parsed.netloc or parsed.query
            or parsed.fragment or parsed.username is not None or parsed.password is not None):
        raise ValueError("REST base URL must be an absolute HTTPS URL without credentials, query or fragment")
    return urlunsplit(("https", parsed.netloc.lower(), parsed.path.rstrip("/"), "", ""))


def approval_envelope(payload: dict[str, Any], target: str, project_root: str) -> dict[str, Any]:
    return {"approval_version": 2, "target": normalize_target(target),
            "method": "POST", "path": POST_PATH,
            "project_root": str(Path(project_root).resolve()), "payload": payload}


def approval_digest(envelope: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(envelope).encode("utf-8")).hexdigest()


def verify_approval(state: Any, approved_digest: str, project_root: str) -> None:
    required = {"approval_version", "target", "method", "path", "project_root", "payload", "digest"}
    if not isinstance(state, dict) or set(state) != required or state.get("approval_version") != 2:
        raise ValueError("approval envelope is unsupported; regenerate preview and obtain approval again")
    if not isinstance(state["target"], str) or not isinstance(state["payload"], dict):
        raise ValueError("invalid approval envelope")
    expected = approval_envelope(state["payload"], state["target"], project_root)
    envelope = {key: value for key, value in state.items() if key != "digest"}
    if envelope != expected or state["digest"] != approved_digest or approval_digest(envelope) != approved_digest:
        raise ValueError("approval envelope integrity or selected project verification failed")
    review_artifact_directory(project_root)
    reject_prohibited(state["payload"])


def require_approved_rest_target(properties_path: Path, approved_target: str) -> None:
    """Fail closed unless execution properties select the approval-bound target."""
    properties: dict[str, str] = {}
    for raw_line in properties_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            properties[key.strip()] = value.strip()
    configured_target = properties.get("restBaseUrl")
    if not configured_target:
        raise ValueError("properties file is missing restBaseUrl")

    if normalize_target(configured_target) != normalize_target(approved_target):
        raise ValueError("REST client properties target does not match the approval-bound target")


def build_payload(rest_operations: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    operations = convert_to_extraction_objects(rest_operations)
    source_type = resolve_source_type(args.source_type)
    setup_text = (
        Path(args.connector_setup_file).read_text(encoding="utf-8")
        if args.connector_setup_file
        else args.connector_setup_json
    )
    setup = json.loads(setup_text)
    openapi_text = (
        Path(args.openapi_spec_file).read_text(encoding="utf-8")
        if args.openapi_spec_file
        else args.openapi_spec_json
    )
    file_contents = json.loads(openapi_text)
    validate_connector_setup(setup)
    if not setup["hostUrl"].startswith("https://") or not setup["accessTokenUrl"].startswith("https://"):
        raise ValueError("connector setup URLs must use HTTPS")
    if not isinstance(file_contents, dict) or not isinstance(file_contents.get("openapi"), str):
        raise ValueError("OpenAPI file contents must be a JSON object with an openapi version")
    validate_openapi_response_schemas(file_contents)
    runtime_id = int(time.time() * 1000)
    setup["source"] = {"id": runtime_id}
    extracted_data = {
        "product": "GRC", "creationStatus": "IN_PROGRESS", "processStatus": "API_SPECIFICATION",
        "connectorStatus": "ACTIVE", "connectorType": "IDENTITY", "incrementalFlag": False,
        "extractionType": "PULL", "editMode": "AUTOMATIC", "sourceTypeName": source_type["sourceTypeName"],
        "sourceTypeCode": source_type["sourceTypeCode"], "name": args.connector_name, "$operation": "CREATE",
        "dataExtractionObjects": operations["dataExtractionObjects"], "sourceEndPoints": operations["sourceEndPoints"],
        "fileName": args.openapi_file_name, "fileContents": file_contents, "source": {"id": runtime_id},
        "jobDefinition": {"scheduledFlag": False, "lastRunCode": 0}, "connectorSetup": setup,
    }
    payload = {"extractedData": extracted_data}
    reject_prohibited(payload)
    return payload


def validate_connector_setup(setup: Any) -> None:
    """Validate the credential-free EPM connector setup contract."""

    if not isinstance(setup, dict):
        raise ValueError("connector setup must be a JSON object")
    unknown = sorted(set(setup) - BASE_CONNECTOR_SETUP_KEYS)
    if unknown:
        raise ValueError("connector setup contains unsupported keys: " + ", ".join(unknown))
    missing = sorted(
        key
        for key in BASE_CONNECTOR_SETUP_KEYS
        if not isinstance(setup.get(key), str) or not setup[key].strip()
    )
    if missing:
        raise ValueError("connector setup is missing required keys: " + ", ".join(missing))
    if not setup["hostUrl"].startswith("https://") or not setup["accessTokenUrl"].startswith("https://"):
        raise ValueError("connector setup URLs must use HTTPS")


def review_artifact_directory(project_root: str) -> Path:
    root = Path(project_root).resolve()
    if not (root / "state" / "project-state.json").is_file():
        raise ValueError("project root must be an initialized FSCR project workspace")
    return artifact_path(root, root / REVIEW_ARTIFACT_DIRECTORY)


def write_state(payload: dict[str, Any], args: argparse.Namespace) -> tuple[Path, str, dict[str, str]]:
    state = approval_envelope(payload, args.target_url, args.project_root)
    digest = approval_digest(state)
    state["digest"] = digest
    if (Path(args.openapi_file_name).name != args.openapi_file_name
            or args.openapi_file_name in {"connector-definition-approval.json", "connector-definition-approval.md"}):
        raise ValueError("OpenAPI file name must be a non-reserved basename")
    current = review_artifact_directory(args.project_root)
    directory = new_preview_directory(current, args.project_root)
    openapi_path = directory / args.openapi_file_name
    approval_path = directory / "connector-definition-approval.json"
    report_path = directory / "connector-definition-approval.md"
    write_new_text(openapi_path, json.dumps(payload["extractedData"]["fileContents"], ensure_ascii=False, indent=2) + "\n", args.project_root)
    write_new_text(approval_path, json.dumps(state, ensure_ascii=False, indent=2) + "\n", args.project_root)
    write_new_text(report_path,
        "# Connector Definition Approval Required\n\n"
        f"Target environment: {state['target']}\n\n"
        f"Operation: {state['method']} {state['path']}\n\n"
        "Review the complete, credential-free payload in `connector-definition-approval.json`.\n\n"
        f"Project workspace: {state['project_root']}\n\n"
        f"Approval envelope SHA-256: `{digest}`\n",
        args.project_root,
    )
    artifacts = {"openapi": str(openapi_path), "approval": str(approval_path), "report": str(report_path)}
    pointer = publish_current_pointer(current, {"approvalState": str(approval_path), "digest": digest, "artifacts": artifacts}, args.project_root)
    return approval_path, digest, {**artifacts, "currentPointer": str(pointer)}


def connector_id_from_response(response: Any) -> str | None:
    """Find the registration ID without printing or persisting the response body."""
    if isinstance(response, dict):
        for key in ("newConnectorId", "connectorId", "id"):
            value = response.get(key)
            if value not in (None, "") and isinstance(value, (str, int)):
                return str(value)
        for value in response.values():
            found = connector_id_from_response(value)
            if found:
                return found
    elif isinstance(response, list):
        for value in response:
            found = connector_id_from_response(value)
            if found:
                return found
    return None


def connector_setup_url(target: str, connector_id: str, setup: dict[str, Any]) -> str:
    """Build the Fusion setup handoff URL with its non-secret assertion fields."""

    query = {"connectorId": connector_id, "connectorType": "EPM"}
    for key in ("assertionUserName", "assertionKeyAlias", "assertionAudienceList"):
        query[key] = unquote(str(setup[key]))
    return (
        target.rstrip("/")
        + "/fscmUI/redwood/rc-dataintegration/rc-ai-datasource/connector-authentication?"
        + urlencode(query)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="EPM connector-definition runner")
    subcommands = parser.add_subparsers(dest="mode", required=True)
    format_parser = subcommands.add_parser("format")
    preview_parser = subcommands.add_parser("preview")
    for command in (format_parser, preview_parser):
        command.add_argument("--input", required=True, help="REST Operations JSON input path")
    preview_parser.add_argument("--target-url", required=True, help="Fusion/Risk Cloud base URL used as the approval target.")
    preview_parser.add_argument("--connector-name", required=True)
    preview_parser.add_argument("--source-type", required=True, choices=("EPM-ARCS", "EPM-FCCS"))
    preview_parser.add_argument("--openapi-file-name", required=True)
    openapi_source = preview_parser.add_mutually_exclusive_group(required=True)
    openapi_source.add_argument("--openapi-spec-json")
    openapi_source.add_argument("--openapi-spec-file")
    preview_parser.add_argument("--project-root", required=True, help="Initialized project workspace; the review-artifact directory is derived automatically.")
    connector_setup = preview_parser.add_mutually_exclusive_group(required=True)
    connector_setup.add_argument("--connector-setup-json")
    connector_setup.add_argument("--connector-setup-file")
    execute_parser = subcommands.add_parser("execute")
    execute_parser.add_argument("--project-root", required=True, help="Selected initialized workspace; must match the approved envelope.")
    execute_parser.add_argument("--approval-state", required=True)
    execute_parser.add_argument("--approve-digest", required=True)
    execute_parser.add_argument("--properties", required=True, help="Fusion/Risk Cloud properties file passed to the shared REST client.")
    args = parser.parse_args()
    try:
        if args.mode in {"format", "preview"}:
            raw_input = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
            rest_operations = json.loads(raw_input)
            if args.mode == "format":
                json.dump(convert_to_extraction_objects(rest_operations), sys.stdout, ensure_ascii=False, indent=2)
                sys.stdout.write("\n")
                return 0
            if Path(args.openapi_file_name).name != args.openapi_file_name:
                raise ValueError("openapi file name must not include a directory path")
            payload = build_payload(rest_operations, args)
            state_path, digest, artifacts = write_state(payload, args)
            print(json.dumps({"approvalRequired": True, "target": args.target_url.rstrip("/"), "method": "POST", "path": POST_PATH, "approvalState": str(state_path), "digest": digest, "artifacts": artifacts}, ensure_ascii=False, indent=2))
            return 0
        args.approval_state = artifact_path(args.project_root, args.approval_state)
        state = json.loads(args.approval_state.read_text(encoding="utf-8"))
        verify_approval(state, args.approve_digest, args.project_root)
        require_approved_rest_target(Path(args.properties), state["target"])
        client = Path(__file__).resolve().parents[6] / "core/fusion-api/rest-api-client/scripts/fusion_rmc_rest_client.py"
        body_path = Path(args.approval_state).with_suffix(".payload.json")
        write_new_text(body_path, json.dumps(state["payload"], ensure_ascii=False) + "\n", args.project_root)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", prefix="epm-connector-response-", delete=False, encoding="utf-8") as response:
            response_path = response.name
        command = [sys.executable, str(client), POST_PATH, "--method", "POST", "--body-file", str(body_path), "--output", response_path, "--properties", args.properties]
        try:
            # Recheck the selected connection immediately before dispatch.
            require_approved_rest_target(Path(args.properties), state["target"])
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                return result.returncode
            registration_response = json.loads(Path(response_path).read_text(encoding="utf-8"))
        finally:
            Path(response_path).unlink(missing_ok=True)
        connector_id = connector_id_from_response(registration_response)
        if not connector_id:
            print("EPM connector runner error: registration response did not contain a connector ID", file=sys.stderr)
            return 2
        print(json.dumps({
            "registration": "submitted",
            "target": state["target"],
            "connectorId": connector_id,
            "sourceType": state["payload"]["extractedData"]["sourceTypeName"],
            "connectorSetupUrl": connector_setup_url(
                state["target"], connector_id, state["payload"]["extractedData"]["connectorSetup"]
            ),
        }, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"EPM connector runner error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
