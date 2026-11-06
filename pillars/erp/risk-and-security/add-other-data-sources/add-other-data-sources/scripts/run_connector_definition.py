#!/usr/bin/env python3
"""Build, approve, and execute a generic connector-definition REST payload."""

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
from urllib.parse import urlsplit, urlunsplit

from openapi_output_formatter import convert_to_extraction_objects

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from openapi_response_schema_validator import validate_openapi_response_schemas
from connector_artifacts import (
    artifact_path, new_preview_directory, publish_current_pointer, write_new_text,
)


POST_PATH = "/api/risk-cloud/rc-tools-ms/dataintegration/v1/dataIntegratorConnectorDefinitions"
PROHIBITED_FIELDS = {"authenticationDetails", "clientSecret", "accessToken", "refreshToken", "privateKey"}
ARTIFACT_DIRECTORY = Path("artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-other-data-sources/current")
SOURCE_TYPE_REGISTRY = Path(__file__).resolve().parents[2] / "connector-source-types.json"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile(path: Path) -> dict[str, Any]:
    profile = load_json(path)
    if not isinstance(profile, dict) or not isinstance(profile.get("connectorType"), str):
        raise ValueError("Connector profile must define connectorType")
    required = profile.get("requiredSetupKeys", [])
    allowed = profile.get("allowedSetupKeys", required)
    if not isinstance(required, list) or not isinstance(allowed, list) or not all(isinstance(x, str) for x in required + allowed):
        raise ValueError("Connector profile setup-key lists must contain strings")
    return profile


def resolve_source_type(connector_type: str) -> dict[str, Any]:
    registry = load_json(SOURCE_TYPE_REGISTRY)
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


def validate_setup(setup: Any, profile: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(setup, dict):
        raise ValueError("Connector setup must be a JSON object")
    required = profile.get("requiredSetupKeys", [])
    allowed = set(profile.get("allowedSetupKeys", required))
    unknown = sorted(set(setup) - allowed)
    if unknown:
        raise ValueError("Connector setup contains unsupported keys: " + ", ".join(unknown))
    missing = [key for key in required if not isinstance(setup.get(key), str) or not setup[key].strip()]
    if missing:
        raise ValueError("Connector setup is missing required keys: " + ", ".join(missing))
    for key in ("hostUrl", "accessTokenUrl"):
        if key in setup and not setup[key].startswith("https://"):
            raise ValueError(f"Connector setup {key} must use HTTPS")
    return setup


def reject_prohibited(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in PROHIBITED_FIELDS:
                raise ValueError(f"Payload contains prohibited field: {key}")
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
    if not (Path(project_root).resolve() / "state" / "project-state.json").is_file():
        raise ValueError("project root must be an initialized FSCR project workspace")
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


def build_payload(operations: Any, openapi_spec: Any, profile: dict[str, Any], connector_name: str, setup: Any) -> dict[str, Any]:
    validate_openapi_response_schemas(openapi_spec)
    extracted = convert_to_extraction_objects(operations)
    setup = validate_setup(setup, profile)
    source_type = resolve_source_type(profile["connectorType"])
    reject_prohibited(openapi_spec)
    runtime_id = int(time.time() * 1000)
    setup = dict(setup)
    setup["source"] = {"id": runtime_id}
    extracted_data = {
        "product": "GRC",
        "creationStatus": "IN_PROGRESS",
        "processStatus": "API_SPECIFICATION",
        "connectorStatus": "ACTIVE",
        "connectorType": "IDENTITY",
        "incrementalFlag": False,
        "extractionType": "PULL",
        "editMode": "AUTOMATIC",
        "sourceTypeName": source_type["sourceTypeName"],
        "sourceTypeCode": source_type["sourceTypeCode"],
        "name": connector_name,
        "$operation": "CREATE",
        "dataExtractionObjects": extracted["dataExtractionObjects"],
        "sourceEndPoints": extracted["sourceEndPoints"],
        "fileName": f"{source_type['sourceTypeName'].lower()}-openapi.json",
        "fileContents": openapi_spec,
        "source": {"id": runtime_id},
        "jobDefinition": {"scheduledFlag": False, "lastRunCode": 0},
        "connectorSetup": setup,
    }
    payload = {"extractedData": extracted_data}
    reject_prohibited(payload)
    return payload


def project_directory(project_root: Path) -> Path:
    root = project_root.resolve()
    if not (root / "state" / "project-state.json").is_file():
        raise ValueError("project root must be an initialized FSCR project workspace")
    return artifact_path(root, root / ARTIFACT_DIRECTORY)


def write_preview(payload: dict[str, Any], project_root: Path, target_url: str) -> dict[str, Any]:
    state = approval_envelope(payload, target_url, str(project_root))
    digest = approval_digest(state)
    state["digest"] = digest
    current = project_directory(project_root)
    directory = new_preview_directory(current, project_root)
    approval_path = directory / "connector-definition-approval.json"
    report_path = directory / "connector-definition-approval.md"
    write_new_text(approval_path, json.dumps(state, ensure_ascii=False, indent=2) + "\n", project_root)
    write_new_text(report_path,
        "# Connector Definition Approval Required\n\n"
        f"Target environment: {state['target']}\n\n"
        f"Operation: POST {POST_PATH}\n\n"
        f"Project workspace: {state['project_root']}\n\n"
        f"Approval envelope SHA-256: `{digest}`\n\n"
        "Review the complete credential-free payload in `connector-definition-approval.json` before approval.\n",
        project_root,
    )
    result = {"approvalRequired": True, "approvalState": str(approval_path), "report": str(report_path), "digest": digest}
    pointer = publish_current_pointer(current, result, project_root)
    return {**result, "currentPointer": str(pointer)}


def connector_id_from_response(response: Any) -> str | None:
    if isinstance(response, dict):
        for key in ("newConnectorId", "connectorId", "id"):
            value = response.get(key)
            if isinstance(value, (str, int)) and str(value):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    format_parser = sub.add_parser("format")
    format_parser.add_argument("--operations", type=Path, required=True)
    format_parser.add_argument("--output", type=Path, required=True)
    preview = sub.add_parser("preview")
    preview.add_argument("--operations", type=Path, required=True)
    preview.add_argument("--openapi-spec", type=Path, required=True)
    preview.add_argument("--profile", type=Path, required=True)
    preview.add_argument("--connector-name", required=True)
    preview.add_argument("--connector-setup-json", type=Path, required=True)
    preview.add_argument("--target-url", required=True)
    preview.add_argument("--project-root", type=Path, required=True)
    execute = sub.add_parser("execute")
    execute.add_argument("--project-root", type=Path, required=True, help="Selected initialized workspace; must match the approved envelope.")
    execute.add_argument("--approval-state", type=Path, required=True)
    execute.add_argument("--approve-digest", required=True)
    execute.add_argument("--properties", type=Path, required=True, help="Fusion/Risk Cloud properties file passed to the shared REST client.")
    args = parser.parse_args()
    try:
        if args.mode == "format":
            formatted = convert_to_extraction_objects(load_json(args.operations))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(formatted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"output": str(args.output.resolve())}, indent=2))
            return 0
        if args.mode == "preview":
            payload = build_payload(
                load_json(args.operations),
                load_json(args.openapi_spec),
                load_profile(args.profile),
                args.connector_name,
                load_json(args.connector_setup_json),
            )
            print(json.dumps(write_preview(payload, args.project_root, args.target_url), indent=2))
            return 0
        args.approval_state = artifact_path(args.project_root, args.approval_state)
        state = load_json(args.approval_state)
        verify_approval(state, args.approve_digest, str(args.project_root))
        require_approved_rest_target(args.properties, state["target"])
        body_path = args.approval_state.with_suffix(".payload.json")
        write_new_text(body_path, json.dumps(state["payload"], ensure_ascii=False), args.project_root)
        client = Path(__file__).resolve().parents[6] / "core/fusion-api/rest-api-client/scripts/fusion_rmc_rest_client.py"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", prefix="connector-definition-response-", delete=False, encoding="utf-8") as response:
            response_path = Path(response.name)
        command = [
            sys.executable,
            str(client),
            POST_PATH,
            "--method",
            "POST",
            "--header",
            "REST-Framework-Version=9",
            "--body-file",
            str(body_path),
            "--properties",
            str(args.properties),
            "--output",
            str(response_path),
        ]
        try:
            # Recheck the selected connection immediately before dispatch.
            require_approved_rest_target(args.properties, state["target"])
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                return result.returncode
            connector_id = connector_id_from_response(load_json(response_path))
        finally:
            response_path.unlink(missing_ok=True)
        if not connector_id:
            raise ValueError("Connector registration response did not contain a connector identifier")
        print(json.dumps({
            "registration": "submitted",
            "target": state["target"],
            "connectorId": connector_id,
            "sourceType": state["payload"]["extractedData"]["sourceTypeName"],
        }, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, TypeError) as exc:
        print(f"Connector definition runner error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
