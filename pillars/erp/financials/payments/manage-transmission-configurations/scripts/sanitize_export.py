#!/usr/bin/env python3
"""Download an already-governed MTC export and persist only sanitized bytes.

No create/import calls. Authentication and transport are reused from core/shared.
The --input mode handles a user-supplied local export without modifying it.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile


def adapter():
    spec = importlib.util.spec_from_file_location("mtc_export_adapter", Path(__file__).with_name("fsm_task_adapter.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sanitize(content, runtime=None):
    m = runtime or adapter()
    c = m._load_contract(m._default_contract_path())
    package = m._read_package(content, c)
    policy = m._mtc_policy()
    configs = m._sensitive.configs_for(package)
    rows = copy.deepcopy(package.rows)
    omitted = []
    for row in rows[m.VALUES]:
        protocol = configs.get(row.get(m.PARENT))
        code = row.get("TransmitParameterCode")
        # The public, task-generated username sentinel is not a customer secret.
        # Keeping this exact literal allows post-import verification of the
        # placeholder while every other username value remains withheld.
        if (any(x["protocol"] == protocol and x["parameter"] == code
                and row.get("TransmitVarchar2Value") == x["value"]
                for x in policy["createPlaceholders"])
                and not any(row.get(c) for c in ("TransmitNumberValue", "TransmitDateValue"))):
            continue
        if m._sensitive.redact_value(policy, protocol, code) or any(
                m._sensitive.suspicious(row.get(col, "")) for col in m.COLS.values()):
            for col in m.COLS.values():
                if row.get(col):
                    omitted.append(row[col])
                    row[col] = m._sensitive.WITHHELD
    # Also suppress recognizable embedded credentials and duplicate secret text
    # in free-form CSV cells; raw source files and model-visible dumps are avoided.
    for values in rows.values():
        for row in values:
            for key, value in row.items():
                if value != m._sensitive.WITHHELD:
                    row[key] = m._sensitive._redact_metadata(value, sorted(set(omitted), key=len, reverse=True))
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as z:
        for entity in c["package"]["entities"]:
            z.writestr(entity["member"], m._csv_bytes(entity["headers"], rows[entity["name"]]))
        metadata = c["package"]["metadataMember"]
        raw_metadata = package.member_bytes[metadata]
        # Metadata should contain no business values. Fail instead of silently
        # changing the FSM schema if a supplied package puts a secret there.
        if any(value.encode("utf-8") in raw_metadata for value in omitted if len(value) >= 8):
            raise ValueError("MTC-EXPORT: Sensitive content in metadata; package not saved.")
        z.writestr(metadata, raw_metadata)
    safe = output.getvalue()
    # Reparse before writing; sanitized snapshots remain exact-shape baselines.
    m._read_package(safe, c)
    return safe, {
        "status": "SANITIZED",
        "sensitivePolicySha256": m._sensitive.digest(),
        "sourceArchiveSha256": m._sha256_bytes(content),
        "sanitizedArchiveSha256": m._sha256_bytes(safe),
        "withheldValueCount": len(omitted),
        "credentialPreservation": "NOT_VERIFIED",
        "importable": False,
    }


def download(args):
    repo = Path(__file__).resolve().parents[6]
    sys.path.insert(0, str(repo / "shared/setup-export/task-level-export/scripts"))
    import get_setup_task_csv_export_result as shared
    from fsm_csv_export_engine import download_result, fusion_rest_json, result_resource
    props = shared.read_properties(Path(args.properties))
    shared.require_props(props, ["environment", "restBaseUrl"])
    token = shared.get_access_token(
        props, open_browser=False, token_cache=args.token_cache, force_login=False,
        callback_timeout=shared.DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    )
    scope = shared.task_scope("IBY_MANAGE_TRANSMISSION_CONFIGURATIONS", template_only=args.template_only)
    process, items = shared.engine_wait_for_result(
        props, token, scope, args.process_id, args.wait_seconds, 10,
    )
    # Some pods expose the completed result by ID while the child collection
    # remains empty. Use the engine's documented singleton resource, never
    # infer success from ProcessCompletedFlag alone or start another export.
    if not items and shared.process_completed(process.get("ProcessCompletedFlag")):
        result = fusion_rest_json(props, result_resource(scope, args.process_id),
                                  access_token=token, query_params={"onlyData": "true"})
        items = [result]
    if shared.status_code(items) not in shared.SUCCESS_STATUS_CODES:
        # Process logs can contain submitted values; do not persist their payload.
        raise ValueError("MTC-EXPORT: Process not successful; inspect details through the governed UI.")
    content, _ = download_result(props, token, scope, args.process_id)
    return content


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--process-id")
    parser.add_argument("--properties")
    parser.add_argument("--token-cache")
    parser.add_argument("--template-only", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = args.output.with_suffix(".sanitization.json")
    try:
        if args.output.exists() or report.exists():
            raise ValueError("Output already exists.")
        if args.process_id and not args.properties:
            raise ValueError("Properties path is required.")
        raw = args.input.read_bytes() if args.input else download(args)
        safe, evidence = sanitize(raw)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(safe)
        report.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(evidence))
        return 0
    except Exception:
        # Never echo source parse/HTTP exceptions, which may contain raw values.
        print(json.dumps({"status": "FAIL", "code": "MTC_EXPORT_SANITIZATION",
                          "message": "No raw export or process log was saved. Check input, authentication, export status and output paths."}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
