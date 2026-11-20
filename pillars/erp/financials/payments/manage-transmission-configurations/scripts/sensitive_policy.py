"""Task-owned MTC policy. No network calls, logging, or raw-value persistence."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

CONFIG = "IBY_TRANSMISSION_CONFIGURATION"
VALUES = "ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL"
PARENT = CONFIG + ".TransmitConfigurationName"
PROTOCOL = "ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL"
COLS = ("TransmitVarchar2Value", "TransmitNumberValue", "TransmitDateValue")
WITHHELD = "[FSCR value withheld]"
POLICY_PATH = Path(__file__).resolve().parents[1] / "ora-resource/sensitive-field-policy.json"


def enabled(contract):
    return contract.get("semanticModel", {}).get("mode") == "task-specific-extension"


def load():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if policy.get("schemaVersion") != 1 or policy.get("defaultHandling") != "manual_omit":
        raise ValueError("MTC-POLICY: Unsupported sensitive-field policy.")
    # Exceptions are developer-maintained classifications, never caller flags.
    for item in policy["createPlaceholders"]:
        p, c = item["protocol"], item["parameter"]
        if (c != "USERNAME" or p not in {"SECURE_FTP_GET", "SECURE_FTP_PUT"}
                or item["value"] != "changeit"):
            raise ValueError("MTC-POLICY: Unsupported create placeholder.")
    for item in policy["ordinaryImportExceptions"]:
        p, c = item["protocol"], item["parameter"]
        if c in policy["alwaysManualParameters"] or c not in policy["reviewedParameterTypes"].get(p, {}):
            raise ValueError("MTC-POLICY: Secrets/key references cannot use an ordinary import exception.")
    return policy


def digest():
    return hashlib.sha256(POLICY_PATH.read_bytes()).hexdigest()


def blocked(policy, protocol, parameter):
    """SecuredFlag supplements semantic classification; unknowns fail closed."""
    if parameter in policy["alwaysManualParameters"]:
        return True
    if parameter not in policy["reviewedParameterTypes"].get(protocol, {}):
        return True
    if any(x["protocol"] == protocol and x["parameter"] == parameter
           for x in policy["ordinaryImportExceptions"]):
        return False
    return (parameter in policy["sensitiveIdentifierParameters"]
            or parameter in policy["sourceFacts"]["protocols"].get(protocol, {}).get("secured", []))


def redact_value(policy, protocol, parameter):
    """Import exceptions never opt out of export protection."""
    without_exceptions = {**policy, "ordinaryImportExceptions": []}
    return blocked(without_exceptions, protocol, parameter)


def configs_for(baseline, operations=()):
    configs = {r["TransmitConfigurationName"]: r["TransmitProtocolCode"]
               for r in baseline.rows[CONFIG]}
    for op in operations:
        if op.get("entity") == CONFIG and op.get("action") == "create":
            configs[op.get("targetKey", {}).get("TransmitConfigurationName")] = op.get("values", {}).get("TransmitProtocolCode")
    return configs


def suspicious(value):
    """Additional guard for recognizable secrets embedded in ordinary text/URLs."""
    text = str(value)
    return bool(re.search(
        r"-----BEGIN (?:[A-Z0-9 ]*PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----"
        r"|://[^/\s:@]+:[^/\s@]+@"
        r"|(?:password|passwd|client_secret|secret_key|access_token|authorization)\s*[:=]\s*\S+",
        text, re.I))


def _redact_metadata(value, omitted):
    if isinstance(value, dict):
        return {k: _redact_metadata(v, omitted) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_metadata(v, omitted) for v in value]
    if isinstance(value, str):
        if suspicious(value):
            return WITHHELD
        for secret in omitted:
            if secret and (value == secret or (len(secret) >= 8 and secret in value)):
                value = value.replace(secret, WITHHELD)
    return value


def prepare(design, baseline):
    """Drop blocked input operations before generic normalization or artifacts."""
    policy = load()
    raw_ops = design.get("operations")
    if not isinstance(raw_ops, list) or not raw_ops or any(not isinstance(op, dict) for op in raw_ops):
        raise ValueError("MTC-POLICY: Input must contain operations.")
    configs = configs_for(baseline, raw_ops)
    params = {(r["TransmitProtocolCode"], r["TransmitParameterCode"]): r
              for r in baseline.rows["ORA_IBY_TRANSMISSION_CONFIG_PARA"]}
    new = {op.get("targetKey", {}).get("TransmitConfigurationName")
           for op in raw_ops if op.get("entity") == CONFIG and op.get("action") == "create"}
    kept, steps, omitted = [], [], []
    for raw in raw_ops:
        if not isinstance(raw, dict):
            raise ValueError("MTC-POLICY: Invalid operation.")
        op = copy.deepcopy(raw)
        target = op.get("targetKey", {})
        name = target.get(PARENT)
        code = target.get("TransmitParameterCode")
        if op.get("entity") == VALUES:
            if name not in configs:
                raise ValueError("MTC-PARENT: Owning configuration is absent.")
            if (configs[name], code) not in params:
                raise ValueError("MTC-PARAMETER: Parameter is absent from target protocol.")
            reviewed_type = policy["reviewedParameterTypes"].get(configs[name], {}).get(code)
            if reviewed_type and reviewed_type != params[(configs[name], code)].get("TransmitParameterType"):
                raise ValueError("MTC-PARAMETER-TYPE: Target datatype differs from reviewed policy.")
        if op.get("entity") == VALUES and blocked(policy, configs.get(name), code):
            omitted.extend(str(v) for v in op.get("values", {}).values() if v not in ("", None))
            steps.append({"configurationName": name, "parameterCode": code,
                          "action": "Complete in Payments UI; supplied value excluded."})
            continue
        if any(suspicious(v) for v in op.get("values", {}).values()):
            raise ValueError("MTC-SENSITIVE-INPUT: Remove embedded credentials from ordinary fields; use Payments UI.")
        kept.append(op)
    if any(secret and (str(value) == secret or (len(secret) >= 8 and secret in str(value)))
           for op in kept for value in op.get("values", {}).values() for secret in omitted):
        raise ValueError("MTC-SENSITIVE-INPUT: An excluded credential was repeated in an ordinary field; remove it before proceeding.")
    kept = _redact_metadata(kept, sorted(set(omitted), key=len, reverse=True))
    existing = {r["TransmitConfigurationName"] for r in baseline.rows[CONFIG]}
    ids = {op.get("id") for op in raw_ops}
    for name in sorted(new - existing):
        protocol = configs[name]
        for item in policy["createPlaceholders"]:
            if item["protocol"] != protocol or not blocked(policy, protocol, item["parameter"]):
                continue
            ident = "MTC-USERNAME-PLACEHOLDER"
            while ident in ids:
                ident += "-1"
            ids.add(ident)
            kept.append({"id": ident, "entity": VALUES, "action": "create",
                         "targetKey": {PARENT: name, "TransmitParameterCode": item["parameter"]},
                         "values": {"TransmitVarchar2Value": item["value"]}})
            steps.append({"configurationName": name, "parameterCode": item["parameter"],
                          "action": "Replace placeholder changeit in Payments UI before use.",
                          "placeholder": "changeit"})
        steps.append({"configurationName": name,
                      "action": "Complete applicable credentials and key setup in Payments UI before use."})
    # User descriptions/warnings/defaults must not reintroduce excluded values.
    clean = _redact_metadata(copy.deepcopy(design), sorted(set(omitted), key=len, reverse=True))
    clean["operations"] = kept
    clean["preservedValues"] = []
    clean["explicitDefaults"] = []  # Derived again from the actual kept operations.
    clean["sensitivePolicySha256"] = digest()
    clean["manualSteps"] = steps
    clean.pop("status", None)
    if not kept:
        clean["status"] = "MANUAL_ONLY"
    return clean


def placeholder_allowed(policy, protocol, code, name, action, values, baseline, operations):
    if action != "create" or any(r["TransmitConfigurationName"] == name for r in baseline.rows[CONFIG]):
        return False
    if not any(op.get("entity") == CONFIG and op.get("action") == "create"
               and op.get("targetKey", {}).get("TransmitConfigurationName") == name for op in operations):
        return False
    match = any(x["protocol"] == protocol and x["parameter"] == code
                and values.get("TransmitVarchar2Value") == x["value"] for x in policy["createPlaceholders"])
    return match and all(values.get(c) in ("", None) for c in COLS[1:])


def check_blueprint(blueprint, baseline):
    policy = load()
    if blueprint.get("sensitivePolicySha256") != digest():
        raise ValueError("MTC-POLICY-STALE: Normalize the design with the current sensitive-field policy.")
    ops = blueprint.get("operations", [])
    configs = configs_for(baseline, ops)
    for op in ops:
        target, values = op.get("targetKey", {}), op.get("values", {})
        if any(suspicious(v) or WITHHELD in str(v) for v in values.values()):
            raise ValueError("MTC-SENSITIVE-INPUT: Sensitive or withheld content is not importable.")
        if op.get("entity") != VALUES:
            continue
        name, code = target.get(PARENT), target.get("TransmitParameterCode")
        protocol = configs.get(name)
        if blocked(policy, protocol, code) and not placeholder_allowed(
                policy, protocol, code, name, op.get("action"), values, baseline, ops):
            raise ValueError("MTC-SENSITIVE-IMPORT: A blocked parameter cannot be imported, cleared or restored.")


def candidate_issues(candidate, baseline, blueprint):
    """Scan every serialized value row, including unrequested/dependency rows."""
    policy = load()
    ops = blueprint.get("operations", [])
    configs = configs_for(baseline, ops)
    issues = []
    if any(suspicious(value) or WITHHELD in str(value)
           for rows in candidate.rows.values() for row in rows for value in row.values()):
        issues.append({"code": "MTC_SENSITIVE_CANDIDATE",
                       "message": "Candidate contains withheld or embedded credential content."})
    for row in candidate.rows[VALUES]:
        name, code = row.get(PARENT), row.get("TransmitParameterCode")
        if (any(row.get(c) == WITHHELD or suspicious(row.get(c, "")) for c in COLS)
            or (blocked(policy, configs.get(name), code) and not placeholder_allowed(
                policy, configs.get(name), code, name, "create", row, baseline, ops))):
            issues.append({"code": "MTC_SENSITIVE_CANDIDATE",
                           "message": "Candidate contains a prohibited parameter-value row; no values displayed."})
    return issues


def safe_report(report, parameter_requirement_ids):
    """Reconciliation may inspect values, but its public matrix never exposes them."""
    result = copy.deepcopy(report)
    for row in result.get("requirementMatrix", []):
        if row.get("requirementId") not in parameter_requirement_ids:
            continue
        for field in ("requested", "candidate", "persisted"):
            if field in row:
                row[field] = "[value comparison withheld]"
        row.pop("rawDifferences", None)
        row.pop("semanticEquivalences", None)
    return result
