#!/usr/bin/env python3
"""Build a validated, credential-free FACPQ setup-task import package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import tempfile
import urllib.parse
import zipfile
from pathlib import Path
from typing import Any


CONFIG = "ORA_ZCA_SALES_TRANS_INTEG_CONFIG.csv"
DETAILS = "ORA_ZCA_SO_SETUP_REF_DETAILS.csv"
REVENUE = "ORA_ZCA_SO_SETUP_DSBL_REV_FLD.csv"
OBJECT_MAP = "ORA_ZCA_SO_SETUP_OBJECT_MAP_VO.csv"
ATTRIBUTE_MAP = "ORA_ZCA_SO_OBJECT_MAP_ATTR_SETUP.csv"
REFERENCE = "ORA_ZCA_SALES_TRANS_INTEG_CONFIG.SetupRefCode"
EXPECTED_CONSUMER = (
    "cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration"
)
ACTIONS = {
    "ZCA_CREATE_TRANSACTION": "CreateQuoteUrl",
    "ZCA_EDIT_TRANSACTION": "EditQuoteUrl",
    "ZCA_COPY_TRANSACTION": "CopyQuoteUrl",
    "ZCA_CREATE_TRANSACTION_VERSION": "CreateVersionUrl",
    "ZCA_GET_PROPOSAL": "GetProposalUrl",
}
SECRET = re.compile(
    r"(?i)(?:username|user|psword|password|secret|token|credential|authorization)\s*="
)
SENSITIVE_FIELD = re.compile(
    r"password|secret|token|credential|authorization", re.IGNORECASE
)
VARIABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
REST_VERSION = re.compile(r"^v[0-9]+$")
POSITIVE_ID = re.compile(r"^[1-9][0-9]*$")
PLACEHOLDER_URL = "https://ThisURLMustBeChanged.com"
PLACEHOLDER_HOSTS = {"thisurlmustbechanged.com"}
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
PROJECTS_ROOT = REPOSITORY_ROOT / "project"


class PackageBuilderError(ValueError):
    """Input, safety, or package-contract failure."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "baseline-zip",
        "manifest",
        "action-contract",
        "setup-ref-code",
        "name",
        "description",
        "fusion-environment",
        "output-zip",
        "preview-output",
    ):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--active", choices=("Y", "N"), default="Y")
    parser.add_argument("--default", choices=("Y", "N"), default="Y")
    parser.add_argument(
        "--revenue-policy", choices=("unrestricted", "restricted"), required=True
    )
    parser.add_argument(
        "--reconciliation-option",
        choices=("ORA_ROOTS", "ORA_PARTS"),
        required=True,
    )
    parser.add_argument(
        "--mapping-policy",
        choices=("preserve-baseline", "leave-empty"),
        default="preserve-baseline",
    )
    parser.add_argument("--deactivate-existing", action="store_true")
    parser.add_argument("--create-if-missing", action="store_true")
    parser.add_argument(
        "--existing-endpoints-file",
        help=(
            "Optional JSON object mapping existing SetupRefCode values to exact "
            "same-target endpoint origins when the baseline contains portable sentinels."
        ),
    )
    parser.add_argument(
        "--overwrite-output",
        action="store_true",
        help="Replace existing package and preview files only after explicit approval.",
    )
    return parser.parse_args(argv)


def csv_read(raw: bytes, label: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not reader.fieldnames:
        raise PackageBuilderError(f"{label} has no CSV header.")
    return list(reader.fieldnames), list(reader)


def csv_write(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def load_json_object(path_value: str, label: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise PackageBuilderError(f"{label} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageBuilderError(f"{label} must be a readable JSON object.") from exc
    if not isinstance(payload, dict):
        raise PackageBuilderError(f"{label} must be a JSON object.")
    return path, payload


def normalize_origin(value: object, label: str) -> str:
    candidate = str(value or "").strip().rstrip("/")
    parsed = urllib.parse.urlsplit(candidate)
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.hostname.lower() in PLACEHOLDER_HOSTS
    ):
        raise PackageBuilderError(
            f"{label} must be one non-placeholder HTTPS origin without credentials or a path."
        )
    port = f":{parsed.port}" if parsed.port else ""
    return f"https://{parsed.hostname}{port}"


def integration_endpoint_from_manifest(params: dict[str, object]) -> str:
    """Return a host-only endpoint when manifest host and endpoint agree."""
    host = normalize_origin(params.get("faHostUrl"), "faHostUrl")
    try:
        endpoint = normalize_origin(
            params.get("facpqEndpointUrl"), "facpqEndpointUrl"
        )
    except PackageBuilderError as exc:
        raise PackageBuilderError(
            "Integration endpoint must exactly equal the Fusion host URL and must not include /cpq."
        ) from exc
    if endpoint != host:
        raise PackageBuilderError(
            "Integration endpoint must exactly equal the Fusion host URL and must not include /cpq."
        )
    return endpoint


def project_path(value: str, overwrite: bool = False) -> Path:
    path = Path(value).expanduser().resolve()
    projects_root = PROJECTS_ROOT.resolve()
    try:
        relative = path.relative_to(projects_root)
    except ValueError as exc:
        raise PackageBuilderError(
            "Output must be inside this repository's project/{project_id} workspace."
        ) from exc
    if len(relative.parts) < 2 or relative.parts[0] == "_template":
        raise PackageBuilderError(
            "Output must name a file in a non-template project/{project_id} workspace."
        )
    project_root = projects_root / relative.parts[0]
    if not (project_root / "state" / "project-state.json").is_file():
        raise PackageBuilderError(
            f"Project workspace is not initialized: {project_root}"
        )
    if path.is_symlink():
        raise PackageBuilderError("Output must not be a symbolic link.")
    if path.exists():
        if not path.is_file():
            raise PackageBuilderError("Output must be a file path.")
        if not overwrite:
            raise PackageBuilderError(
                "Output already exists; use --overwrite-output only after explicit approval."
            )
    return path


def validate_manifest(
    manifest: dict[str, Any], fusion_environment: str
) -> dict[str, str]:
    if manifest.get("status") != "ready" or manifest.get("completeness") != "complete":
        raise PackageBuilderError(
            "Metadata manifest must have status ready and completeness complete."
        )
    boundaries = manifest.get("boundaries")
    if (
        not isinstance(boundaries, dict)
        or boundaries.get("facpq_mutations") is not False
        or boundaries.get("allowed_facpq_methods") != ["GET"]
        or boundaries.get("bm_cpq_supported") is not False
        or boundaries.get("consumer") != EXPECTED_CONSUMER
    ):
        raise PackageBuilderError(
            "Metadata manifest must declare the GET-only FACPQ consumer boundary."
        )
    params = manifest.get("parameters")
    if not isinstance(params, dict):
        raise PackageBuilderError("Metadata manifest must contain a parameters object.")
    required = (
        "faHostUrl",
        "facpqEndpointUrl",
        "restFrameworkVersion",
        "processName",
        "documentName",
        "documentId",
        "copyActionId",
        "versionActionId",
    )
    missing = [field for field in required if not str(params.get(field) or "").strip()]
    if missing:
        raise PackageBuilderError(
            "Metadata manifest is missing: " + ", ".join(missing) + "."
        )
    host = normalize_origin(params["faHostUrl"], "faHostUrl")
    endpoint = normalize_origin(params["facpqEndpointUrl"], "facpqEndpointUrl")
    environment = normalize_origin(fusion_environment, "fusion-environment")
    if endpoint != host or environment != host:
        raise PackageBuilderError(
            "fusion-environment, faHostUrl, and facpqEndpointUrl must identify the same Fusion origin."
        )
    rest_version = str(params["restFrameworkVersion"]).strip().lower()
    if not REST_VERSION.fullmatch(rest_version):
        raise PackageBuilderError("restFrameworkVersion must use v<number> syntax.")
    normalized = {
        "faHostUrl": host,
        "facpqEndpointUrl": endpoint,
        "restFrameworkVersion": rest_version,
    }
    for field in ("processName", "documentName"):
        value = str(params[field]).strip()
        if not VARIABLE_NAME.fullmatch(value):
            raise PackageBuilderError(f"{field} must be an exact FACPQ variable name.")
        normalized[field] = value
    for field in ("documentId", "copyActionId", "versionActionId"):
        value = str(params[field]).strip()
        if not POSITIVE_ID.fullmatch(value):
            raise PackageBuilderError(f"{field} must be a positive numeric identifier.")
        normalized[field] = value
    return normalized


def expected_action_urls(params: dict[str, str]) -> dict[str, str]:
    process = params["processName"]
    document_id = params["documentId"]
    copy_action_id = params["copyActionId"]
    version_action_id = params["versionActionId"]
    return {
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


def validate_action_contract(
    contract: dict[str, Any], contract_path: Path, manifest_path: Path, params: dict[str, str]
) -> dict[str, str]:
    if (
        contract.get("status") != "ready"
        or contract.get("platform") != "FACPQ"
        or contract.get("sso_family") != "oidc"
    ):
        raise PackageBuilderError(
            "Action contract must be a ready FACPQ OpenID Connect contract."
        )
    boundaries = contract.get("boundaries")
    if (
        not isinstance(boundaries, dict)
        or boundaries.get("network_requests") is not False
        or boundaries.get("facpq_mutations") is not False
        or boundaries.get("bm_cpq_supported") is not False
        or boundaries.get("fusion_mutations") is not False
    ):
        raise PackageBuilderError(
            "Action contract must declare the non-mutating FACPQ boundary."
        )
    source_manifest = contract.get("source_manifest")
    if (
        not source_manifest
        or Path(str(source_manifest)).expanduser().resolve() != manifest_path.resolve()
    ):
        raise PackageBuilderError(
            f"Action contract {contract_path} is not bound to the selected metadata manifest."
        )
    actual = contract.get("action_urls")
    expected = expected_action_urls(params)
    if actual != expected:
        raise PackageBuilderError(
            "Action contract values do not exactly match the fixed FACPQ OpenID Connect expressions."
        )
    return expected


def load_existing_endpoints(path_value: str | None, target_host: str) -> dict[str, str]:
    if not path_value:
        return {}
    _, payload = load_json_object(path_value, "Existing endpoint evidence")
    endpoints: dict[str, str] = {}
    for raw_reference, raw_endpoint in payload.items():
        reference = str(raw_reference).strip()
        if not reference:
            raise PackageBuilderError("Existing endpoint evidence contains a blank reference code.")
        endpoint = normalize_origin(raw_endpoint, f"Endpoint for {reference}")
        if endpoint != target_host:
            raise PackageBuilderError(
                f"Endpoint evidence for {reference} does not match the selected Fusion origin."
            )
        endpoints[reference] = endpoint
    return endpoints


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def temporary_output(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    return Path(name)


def publish_output(temp_path: Path, destination: Path, overwrite: bool) -> None:
    if overwrite:
        os.replace(temp_path, destination)
        return
    try:
        os.link(temp_path, destination)
    except FileExistsError as exc:
        raise PackageBuilderError(
            "Output appeared after preflight; obtain approval before overwriting it."
        ) from exc
    finally:
        temp_path.unlink(missing_ok=True)


def redacted_value(field: str, value: str | None) -> str | None:
    return "[REDACTED]" if SENSITIVE_FIELD.search(field) and value else value


def config_deltas(
    fields: list[str], before_rows: list[dict[str, str]], after_rows: list[dict[str, str]]
) -> list[dict[str, Any]]:
    before_by_reference = {row.get("SetupRefCode", ""): row for row in before_rows}
    deltas: list[dict[str, Any]] = []
    for row in after_rows:
        reference = row.get("SetupRefCode", "")
        before = before_by_reference.get(reference)
        changes: dict[str, dict[str, str | None]] = {}
        for field in fields:
            old_value = before.get(field, "") if before is not None else None
            new_value = row.get(field, "")
            if old_value != new_value:
                changes[field] = {
                    "before": redacted_value(field, old_value),
                    "after": redacted_value(field, new_value),
                }
        if changes:
            deltas.append(
                {
                    "setup_ref_code": reference,
                    "operation": "create" if before is None else "update",
                    "changes": changes,
                }
            )
    return deltas


def build_package(value: argparse.Namespace) -> dict[str, Any]:
    manifest_path, manifest = load_json_object(value.manifest, "Metadata manifest")
    contract_path, contract = load_json_object(value.action_contract, "Action contract")
    params = validate_manifest(manifest, value.fusion_environment)
    urls = validate_action_contract(contract, contract_path, manifest_path, params)
    endpoint_evidence = load_existing_endpoints(
        value.existing_endpoints_file, params["faHostUrl"]
    )

    baseline_path = Path(value.baseline_zip).expanduser().resolve()
    if not baseline_path.is_file():
        raise PackageBuilderError(f"Baseline ZIP does not exist: {baseline_path}")
    package_path = project_path(value.output_zip, value.overwrite_output)
    preview_path = project_path(value.preview_output, value.overwrite_output)
    if package_path == preview_path:
        raise PackageBuilderError("Package and preview outputs must be different files.")

    package_temp = temporary_output(package_path)
    preview_temp = temporary_output(preview_path)
    try:
        replacements: dict[str, bytes] = {}
        with zipfile.ZipFile(baseline_path) as baseline:
            names = baseline.namelist()
            required_files = (CONFIG, DETAILS, REVENUE, OBJECT_MAP, ATTRIBUTE_MAP)
            missing_files = [name for name in required_files if name not in names]
            if missing_files:
                raise PackageBuilderError(
                    "Baseline ZIP is missing: " + ", ".join(missing_files) + "."
                )
            fields, rows = csv_read(baseline.read(CONFIG), CONFIG)
            required_fields = {
                "SetupRefCode",
                "ActiveFlag",
                "DefaultFlag",
                "Name",
                "Description",
                "EndPointUrl",
                "DocumentName",
                "ProcessName",
                "RestFrameworkVersion",
                "RevnReconcileOption",
            }
            missing_fields = sorted(required_fields - set(fields))
            if missing_fields:
                raise PackageBuilderError(
                    f"{CONFIG} is missing columns: " + ", ".join(missing_fields) + "."
                )
            before_rows = [dict(row) for row in rows]
            target_rows = [
                row for row in rows if row.get("SetupRefCode") == value.setup_ref_code
            ]
            created = False
            if not target_rows and value.create_if_missing:
                target = {field: "" for field in fields}
                target.update(
                    {
                        "SetupRefCode": value.setup_ref_code,
                        "OptInRevnSync": "N",
                        "RelatedObjectTypeCd": "SalesOrdersSetupRef",
                    }
                )
                rows.append(target)
                target_rows = [target]
                created = True
            if len(target_rows) != 1:
                raise PackageBuilderError(
                    f"Expected exactly one row for {value.setup_ref_code!r}; found {len(target_rows)}."
                )
            target = target_rows[0]
            deactivated: list[str] = []
            if value.deactivate_existing:
                for row in rows:
                    if row is target:
                        continue
                    reference = row.get("SetupRefCode", "")
                    if row.get("ActiveFlag") == "Y":
                        row["ActiveFlag"] = "N"
                        deactivated.append(reference)
                    if row.get("DefaultFlag") == "Y":
                        row["DefaultFlag"] = "N"

            endpoint_evidence_used: list[str] = []
            for row in rows:
                if row is target or row.get("EndPointUrl") != PLACEHOLDER_URL:
                    continue
                reference = row.get("SetupRefCode", "")
                resolved_endpoint = endpoint_evidence.get(reference)
                if not resolved_endpoint:
                    raise PackageBuilderError(
                        f"Baseline row {reference!r} contains the portable endpoint sentinel; "
                        "provide exact same-target evidence through --existing-endpoints-file."
                    )
                row["EndPointUrl"] = resolved_endpoint
                endpoint_evidence_used.append(reference)

            target.update(
                {
                    "ActiveFlag": value.active,
                    "DefaultFlag": value.default,
                    "Name": value.name,
                    "Description": value.description,
                    "EndPointUrl": params["facpqEndpointUrl"],
                    "DocumentName": params["documentName"],
                    "ProcessName": params["processName"],
                    "RestFrameworkVersion": params["restFrameworkVersion"],
                    "RevnReconcileOption": value.reconciliation_option,
                }
            )
            replacements[CONFIG] = csv_write(fields, rows)

            detail_fields, detail_rows = csv_read(baseline.read(DETAILS), DETAILS)
            replaced = sum(
                row.get(REFERENCE) == value.setup_ref_code
                and row.get("ProcessParameterName") in ACTIONS
                for row in detail_rows
            )
            detail_rows = [
                row for row in detail_rows if row.get(REFERENCE) != value.setup_ref_code
            ]
            detail_rows.extend(
                {
                    REFERENCE: value.setup_ref_code,
                    "ProcessParameterName": key,
                    "ProcessParameterValue": urls[url_key],
                }
                for key, url_key in ACTIONS.items()
            )
            replacements[DETAILS] = csv_write(detail_fields, detail_rows)

            revenue_fields, revenue_rows = csv_read(baseline.read(REVENUE), REVENUE)
            if value.revenue_policy == "unrestricted":
                revenue_rows = [
                    row
                    for row in revenue_rows
                    if row.get(REFERENCE) != value.setup_ref_code
                ]
            replacements[REVENUE] = csv_write(revenue_fields, revenue_rows)
            if value.mapping_policy == "leave-empty":
                for filename in (OBJECT_MAP, ATTRIBUTE_MAP):
                    map_fields, map_rows = csv_read(baseline.read(filename), filename)
                    replacements[filename] = csv_write(
                        map_fields,
                        [
                            row
                            for row in map_rows
                            if row.get(REFERENCE) != value.setup_ref_code
                        ],
                    )
            with zipfile.ZipFile(
                package_temp, "w", compression=zipfile.ZIP_DEFLATED
            ) as output:
                for name in names:
                    output.writestr(name, replacements.get(name, baseline.read(name)))

        with zipfile.ZipFile(package_temp) as package:
            package_text = "\n".join(
                package.read(name).decode("utf-8", errors="ignore")
                for name in package.namelist()
                if name.lower().endswith((".csv", ".xml", ".txt"))
            )
            object_rows = sum(
                row.get(REFERENCE) == value.setup_ref_code
                for row in csv_read(package.read(OBJECT_MAP), OBJECT_MAP)[1]
            )
            attribute_rows = sum(
                row.get(REFERENCE) == value.setup_ref_code
                for row in csv_read(package.read(ATTRIBUTE_MAP), ATTRIBUTE_MAP)[1]
            )
        if SECRET.search(package_text):
            raise PackageBuilderError(
                "Credential-like content remains in the generated package."
            )
        if PLACEHOLDER_URL in package_text:
            raise PackageBuilderError(
                "The generated package still contains the portable endpoint sentinel."
            )

        digest = sha256_file(package_temp)
        preview = {
            "status": "ready_for_approval",
            "environment": params["faHostUrl"],
            "task_code": "ORA_ZCA_OSC_CPQ_INTEGRATION",
            "setup_ref_code": value.setup_ref_code,
            "name": value.name,
            "description": value.description,
            "facpq_endpoint": params["facpqEndpointUrl"],
            "process_name": target["ProcessName"],
            "document_name": target["DocumentName"],
            "rest_framework_version": target["RestFrameworkVersion"],
            "active": value.active == "Y",
            "default": value.default == "Y",
            "revenue_policy": value.revenue_policy,
            "reconciliation_option": value.reconciliation_option,
            "mapping_policy": value.mapping_policy,
            "object_mapping_rows": object_rows,
            "attribute_mapping_rows": attribute_rows,
            "instance_created": created,
            "deactivate_existing": value.deactivate_existing,
            "deactivated_existing_integration_ref_codes": deactivated,
            "existing_endpoint_evidence_used": sorted(endpoint_evidence_used),
            "configuration_row_deltas": config_deltas(fields, before_rows, rows),
            "existing_action_rows_replaced": replaced,
            "action_rows_written": len(ACTIONS),
            "action_parameter_names": list(ACTIONS),
            "action_urls": urls,
            "credentials_present": False,
            "package_path": str(package_path),
            "package_sha256": digest,
            "source_sha256": {
                "baseline_zip": sha256_file(baseline_path),
                "metadata_manifest": sha256_file(manifest_path),
                "action_contract": sha256_file(contract_path),
            },
            "overwrite_approved": value.overwrite_output,
            "approval_required": True,
        }
        preview_temp.write_text(
            json.dumps(preview, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        publish_output(package_temp, package_path, value.overwrite_output)
        publish_output(preview_temp, preview_path, value.overwrite_output)
        return preview
    finally:
        package_temp.unlink(missing_ok=True)
        preview_temp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    try:
        preview = build_package(parse_args(argv))
        print(json.dumps(preview, indent=2, sort_keys=True))
        return 0
    except (PackageBuilderError, OSError, UnicodeError, zipfile.BadZipFile) as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "failure_class": "input_validation",
                    "message": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
