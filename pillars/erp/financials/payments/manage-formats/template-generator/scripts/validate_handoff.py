"""Validate a Manage Formats template handoff against project artifacts.

This is a read-only domain check. Project artifact registration and state writes
remain owned by the declared core project-management skills.
"""

import argparse
import hashlib
import json
from pathlib import Path


ENGINE_USAGES = {
    "erp.financials.payments.manage-formats.template-generator.bank-iso": "Funds Disbursement",
    "erp.financials.payments.manage-formats.template-generator.avs-provider": "Account Validation Service",
    "erp.financials.payments.manage-formats.template-generator.virtual-card-provider": "Virtual Card Payments",
}
ENGINE_IDS = set(ENGINE_USAGES)
REQUIRED_KINDS = {"template", "mapping_matrix", "source_gaps", "offline_validation"}
RECORD_KEYS = {"artifactIndexPath", "skillRunPath", "tokenUsagePath"}
ALLOWED_FOLDERS = {"artifacts", "exports", "baselines", "decisions", "blueprints", "state"}


def project_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("missing project-relative path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.parts[0] not in ALLOWED_FOLDERS:
        raise ValueError(f"unsafe project path: {relative}")
    root = root.resolve()
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError(f"missing or escaping project file: {relative}")
    return resolved


def validate(handoff: dict, project_root: Path) -> list[str]:
    errors = []
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["artifact_persistence: jsonschema is required to validate the handoff contract"]
    schema = json.loads((Path(__file__).resolve().parents[1] / "references/template-handoff.schema.json").read_text(encoding="utf-8"))
    schema_errors = list(Draft202012Validator(schema).iter_errors(handoff))
    if schema_errors:
        # Do not echo rejected payload values into diagnostics.
        return ["input_validation: handoff schema violation at " + "/".join(map(str, error.absolute_path)) for error in schema_errors]
    required = {
        "schemaVersion", "projectId", "assistanceMode", "recordOwner", "formatCode",
        "formatTypeCode", "usageType", "engineSkillId", "attachmentMechanism",
        "generationStatus", "attachmentStatus", "runtimeVerificationStatus",
        "artifacts", "gaps", "nextAction", "projectRecords",
    }
    for name in sorted(required - handoff.keys()):
        errors.append(f"missing field: {name}")
    if errors:
        return errors
    if handoff["schemaVersion"] not in {"fscr-payments-template-handoff-v2", "fscr-payments-template-handoff-v3"}:
        errors.append("unsupported handoff schema version")
    for field in ("formatCode", "formatTypeCode"):
        if handoff[field] is not None and (not isinstance(handoff[field], str) or not 1 <= len(handoff[field]) <= 30):
            errors.append(f"{field} must be 1 to 30 characters")
    if not isinstance(handoff["nextAction"], str) or not handoff["nextAction"]:
        errors.append("nextAction is required")
    if not isinstance(handoff["gaps"], list):
        errors.append("gaps must be a list")
    if handoff["projectId"] != project_root.name:
        errors.append("handoff projectId does not match project directory")
    if handoff["assistanceMode"] not in {"generated", "guided-manual", "disabled"}:
        errors.append("invalid assistance mode")
    if handoff["recordOwner"] not in {"generator", "manage_formats"}:
        errors.append("invalid record owner")
    if handoff["generationStatus"] not in {"discovery", "draft", "validated", "failed", "disabled"}:
        errors.append("invalid generation status")
    if handoff["attachmentMechanism"] not in {"direct_xml_upload", "bi_publisher_selection", "unknown"}:
        errors.append("invalid attachment mechanism")
    if handoff["attachmentStatus"] not in {"pending_manual_upload", "pending_bi_selection", "attached_confirmed", "not_applicable", "pending_route_confirmation"}:
        errors.append("invalid attachment status")
    if handoff["runtimeVerificationStatus"] not in {"pending", "passed", "failed"}:
        errors.append("invalid runtime verification status")
    if handoff["assistanceMode"] == "disabled" and handoff["generationStatus"] != "disabled":
        errors.append("disabled assistance cannot claim generation")
    if handoff["assistanceMode"] == "guided-manual" and handoff["generationStatus"] not in {"discovery", "draft", "failed"}:
        errors.append("guided manual assistance cannot claim validated generation")
    if handoff["generationStatus"] == "validated" and handoff["engineSkillId"] not in ENGINE_IDS:
        errors.append("validated generation requires a packaged engine skill")
    if handoff["generationStatus"] == "validated" and ENGINE_USAGES.get(handoff["engineSkillId"]) != handoff["usageType"]:
        errors.append("validated generation route does not match usage type")
    if handoff["recordOwner"] == "generator":
        expected = {"direct_xml_upload": "pending_manual_upload", "bi_publisher_selection": "pending_bi_selection", "unknown": "pending_route_confirmation"}.get(handoff["attachmentMechanism"])
        if handoff["attachmentStatus"] != expected:
            errors.append("generator cannot confirm Fusion attachment")
        if handoff["runtimeVerificationStatus"] != "pending":
            errors.append("generator cannot confirm runtime verification")
    if handoff["attachmentStatus"] == "attached_confirmed" or handoff["runtimeVerificationStatus"] == "passed":
        if handoff["recordOwner"] != "manage_formats" or not handoff.get("evidenceReferences"):
            errors.append("confirmed attachment or runtime requires parent evidence")
    if handoff["runtimeVerificationStatus"] == "passed" and handoff["attachmentStatus"] != "attached_confirmed":
        errors.append("runtime cannot pass before attachment is confirmed")
    if handoff["generationStatus"] == "failed" and (
        handoff.get("failureClass") not in {
            "input_validation", "catalog_or_metadata_mismatch", "artifact_persistence", "process_failed"
        } or not handoff.get("diagnostic")
    ):
        errors.append("failed generation requires failureClass and diagnostic")
    if not isinstance(handoff["artifacts"], list):
        return errors + ["artifacts must be a list"]

    kinds = set()
    template_hashes = set()
    locations = set()
    for artifact in handoff["artifacts"]:
        if not isinstance(artifact, dict) or not {"kind", "path", "sha256"} <= artifact.keys():
            errors.append("artifact requires kind, path, and sha256")
            continue
        if artifact["kind"] not in {"template", "mapping_matrix", "source_gaps", "offline_validation", "discovery_pack"}:
            errors.append(f"unsupported artifact kind: {artifact['kind']}")
        kinds.add(artifact["kind"])
        locations.add(artifact["path"])
        try:
            file = project_file(project_root, artifact["path"])
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            if artifact["sha256"] != digest:
                errors.append(f"artifact checksum mismatch: {artifact['path']}")
            if artifact["kind"] == "template":
                template_hashes.add(digest)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    # A delivered draft template needs the same traceable file bundle; readiness remains separate.
    template_bundle = handoff["generationStatus"] == "validated" or (
        handoff["schemaVersion"] == "fscr-payments-template-handoff-v3" and "template" in kinds
    )
    if template_bundle:
        for kind in sorted(REQUIRED_KINDS - kinds):
            errors.append(f"template handoff lacks {kind} artifact")
        if handoff.get("templateSha256") not in template_hashes:
            errors.append("primary template hash does not match a template artifact")
        if not handoff.get("templateIdentity"):
            errors.append("template handoff lacks template identity")

    records = handoff["projectRecords"]
    if not isinstance(records, dict) or not RECORD_KEYS <= records.keys():
        return errors + ["projectRecords lacks artifact index, skill run, or token usage path"]
    for name in sorted(RECORD_KEYS):
        try:
            project_file(project_root, records[name])
        except (ValueError, OSError) as exc:
            errors.append(f"{name}: {exc}")
    try:
        index = json.loads(project_file(project_root, records["artifactIndexPath"]).read_text(encoding="utf-8"))
        if index.get("project_id") != handoff["projectId"]:
            errors.append("artifact index project_id mismatch")
        registered = {}
        for row in index.get("artifacts", []):
            if isinstance(row, dict):
                location = row.get("location", "").removeprefix(f"project/{handoff['projectId']}/")
                registered.setdefault(location, []).append(row)
        for missing in sorted(locations - set(registered)):
            errors.append(f"artifact not registered: {missing}")
        for artifact in handoff["artifacts"]:
            rows = registered.get(artifact["path"], [])
            if len(rows) != 1 or rows[0].get("checksum") != artifact["sha256"]:
                errors.append(f"artifact registry checksum or identity mismatch: {artifact['path']}")
        for evidence in handoff.get("evidenceReferences", []):
            file = project_file(project_root, evidence)
            rows = registered.get(evidence, [])
            if len(rows) != 1 or rows[0].get("checksum") != hashlib.sha256(file.read_bytes()).hexdigest():
                errors.append("parent evidence must have one matching registered checksum")
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot inspect artifact index: {exc}")
    try:
        run = json.loads(project_file(project_root, records["skillRunPath"]).read_text(encoding="utf-8"))
        required_run = {"run_id", "skill_id", "started_at", "status", "inputs", "outputs", "artifact_refs"}
        if not isinstance(run, dict) or not required_run <= run.keys():
            errors.append("skill run record lacks required FSCR fields")
        else:
            expected_owner = handoff["engineSkillId"] or "erp.financials.payments.manage-formats.template-generator"
            allowed_owners = {expected_owner}
            if handoff["recordOwner"] == "manage_formats":
                allowed_owners.add("erp.financials.payments.manage-formats")
            if run["skill_id"] not in allowed_owners:
                errors.append("skill run owner does not match handoff")
            refs = run["artifact_refs"]
            if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
                errors.append("skill run artifact_refs must be a string list")
            elif not locations <= {ref.removeprefix(f"project/{handoff['projectId']}/") for ref in refs}:
                errors.append("skill run does not reference every handoff artifact")
            if handoff["generationStatus"] == "validated" and run["status"] != "completed":
                errors.append("validated generation requires a completed skill run")
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot inspect skill run: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.handoff.read_text(encoding="utf-8"))
        errors = validate(data, args.project_root)
    except (OSError, ValueError, TypeError, AttributeError):
        errors = ["input_validation: unreadable or malformed handoff/project record"]
    for error in errors:
        print(error)
    if errors:
        return 1
    print("Template handoff and project artifacts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
