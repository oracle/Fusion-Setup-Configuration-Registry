"""MPS task-owned sensitive-row policy; offline, no logging or secret persistence."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = "IBY_PAYMENT_SYSTEM"
PARENT = ROOT + ".Suffix"
DEFINITION = "ORA_IBY_PAYMENT_SYSTEM_ACC_NAME"
VALUE = "ORA_IBY_PAYMENT_SYSTEM_ACC_VAL"
POLICY_PATH = Path(__file__).resolve().parents[1] / "references/sensitive-policy.json"
WITHHELD = "[FSCR value withheld]"


def load():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if (policy.get("schemaVersion") != "mps-sensitive-policy-v1"
            or policy.get("manualUntilSupportedSecureFramework") is not True
            or policy.get("placeholderAllowlist") != []
            or policy.get("maskReplayAllowed") is not False
            or policy.get("credentialReplayAllowed") is not False):
        raise ValueError("MPS-POLICY: Unsupported sensitive-field policy.")
    return policy


def digest():
    load()
    # Lifecycle rules also affect whether an otherwise ordinary row is safe to serialize.
    return hashlib.sha256(POLICY_PATH.read_bytes() + b"\x00" + POLICY_PATH.with_name("lifecycle-policy.json").read_bytes()).hexdigest()


def suspicious(value):
    return bool(re.search(
        r"-----BEGIN (?:[A-Z0-9 ]*PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----"
        r"|://[^/\s:@]+:[^/\s@]+@"
        r"|(?:password|passwd|client_secret|access_token|authorization)\s*[:=]\s*\S+",
        str(value), re.I))


def _index(rows, fields):
    result = {}
    for row in rows:
        key = tuple(row.get(field) for field in fields)
        if any(value in (None, "") for value in key) or key in result:
            raise ValueError("MPS-POLICY: Missing or ambiguous owning identity.")
        result[key] = row
    return result


def definitions(baseline, operations=()):
    before = _index(baseline.rows[DEFINITION], (PARENT, "AccountOptionCode"))
    effective = copy.deepcopy(before)
    for op in operations:
        if op.get("entity") != DEFINITION:
            continue
        target = op.get("targetKey", {})
        key = (target.get(PARENT), target.get("AccountOptionCode"))
        effective[key] = {**effective.get(key, {}), **target, **op.get("values", {})}
    return before, effective


def blocked(policy, key, before, effective):
    """Null segment IDs and SecuredFlag=N alone never establish safety."""
    reviewed = policy.get("reviewedOrdinaryOptionCodes", {})
    if not reviewed.get(key[1], {}).get("sourceIds"):
        return True
    row = effective.get(key)
    if row is None:
        return True
    for definition in [row] + ([before[key]] if key in before else []):
        if definition.get("SecuredFlag") != "N" or definition.get("TopologyMgrCode") not in ("", None):
            return True
    return False


def _owner(op):
    return op.get("targetKey", {}).get("Suffix" if op.get("entity") == ROOT else PARENT)


def check_roots(operations, baseline, policy):
    roots = _index(baseline.rows[ROOT], ("Suffix",))
    new_roots = {_owner(op) for op in operations if op.get("entity") == ROOT and op.get("action") == "create"}
    accounts = set(_index(baseline.rows["ORA_IBY_PAYMENT_SYSTEM_KEY"], (PARENT, "Key1")))
    accounts.update((op.get("targetKey", {}).get(PARENT), op.get("targetKey", {}).get("Key1"))
                    for op in operations if op.get("entity") == "ORA_IBY_PAYMENT_SYSTEM_KEY" and op.get("action") == "create")
    for op in operations:
        owner = _owner(op)
        row = roots.get((owner,))
        if row is None and owner not in new_roots:
            raise ValueError("MPS-ROOT: Owning payment system needs a complete current baseline or explicit create operation.")
        if row is not None and any(row.get(field) != "" for field in policy["rootCredentialFields"]):
            raise ValueError("MPS-ROOT-MANUAL: Root credential state prevents safe subtree serialization; use Payments UI for this system.")
        if op.get("entity") == ROOT and any(field in op.get("values", {}) for field in policy["rootCredentialFields"]):
            raise ValueError("MPS-ROOT-MANUAL: Credential changes, including blanks, require Payments UI.")
        if op.get("entity") == VALUE and (owner, op.get("targetKey", {}).get("ORA_IBY_PAYMENT_SYSTEM_KEY.Key1")) not in accounts:
            raise ValueError("MPS-ACCOUNT: Exact owning account must exist or be explicitly created in this request.")


def _redact(value, secrets):
    if isinstance(value, dict):
        return {key: _redact(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, str):
        if suspicious(value):
            return WITHHELD
        for secret in secrets:
            if secret and secret in value:
                value = value.replace(secret, WITHHELD)
    return value


def prepare(design, baseline):
    policy = load()
    ops = design.get("operations")
    if not isinstance(ops, list) or not ops or any(not isinstance(op, dict) for op in ops):
        raise ValueError("MPS-POLICY: Input must contain operations.")
    before, effective = definitions(baseline, ops)
    kept, manual, secrets = [], [], []
    for op in ops:
        target = op.get("targetKey", {})
        key = (target.get(PARENT), target.get("AccountOptionCode"))
        if op.get("entity") == VALUE and blocked(policy, key, before, effective):
            secrets.extend(str(v) for v in op.get("values", {}).values() if v not in (None, ""))
            manual.append({"entity": VALUE, "targetKey": target,
                           "action": "Complete this setting in Payments UI; entire value row excluded from import."})
        else:
            kept.append(copy.deepcopy(op))
    check_roots(kept, baseline, policy)
    clean = _redact(copy.deepcopy(design), sorted(set(secrets), key=len, reverse=True))
    clean["operations"] = _redact(kept, sorted(set(secrets), key=len, reverse=True))
    clean["manualSteps"] = _redact(manual, sorted(set(secrets), key=len, reverse=True))
    clean["sensitivePolicySha256"] = digest()
    clean["preservedValues"] = []
    clean["explicitDefaults"] = []
    clean["status"] = "READY" if kept else "MANUAL_ONLY"
    return clean


def check_blueprint(blueprint, baseline):
    policy = load()
    if blueprint.get("sensitivePolicySha256") != digest():
        raise ValueError("MPS-POLICY-STALE: Normalize with the current sensitive policy.")
    ops = blueprint.get("operations", [])
    check_roots(ops, baseline, policy)
    before, effective = definitions(baseline, ops)
    for op in ops:
        values, target = op.get("values", {}), op.get("targetKey", {})
        if any(suspicious(v) or WITHHELD in str(v) for v in values.values()):
            raise ValueError("MPS-SENSITIVE: Embedded or withheld credentials cannot be imported.")
        if op.get("entity") == VALUE:
            if blocked(policy, (target.get(PARENT), target.get("AccountOptionCode")), before, effective):
                raise ValueError("MPS-SENSITIVE: Sensitive or unclassified value rows cannot be imported or restored.")
            value = values.get("AccountOptionValue")
            if value is not None and (not str(value).strip() or set(str(value)) == {"*"}):
                raise ValueError("MPS-VALUE: Blank or masked account values cannot be replayed.")
            if target.get("AccountOptionCode") == "BU_NAME" and value is not None and not values.get("BuName"):
                raise ValueError("MPS-BU: Supply the business unit name through BuName; do not author a database ID as AccountOptionValue.")
            rule = policy["reviewedOrdinaryOptionCodes"][target["AccountOptionCode"]]
            resolver = rule.get("resolverRequirement")
            if resolver:
                receipts = [item for item in blueprint.get("optionResolutionEvidence", [])
                            if isinstance(item, dict) and item.get("operationId") == op.get("id")]
                if len(receipts) != 1:
                    raise ValueError("MPS-RESOLVER: Exact option resolution evidence is required.")
                receipt = receipts[0]
                expected_value = values.get("BuName") if target.get("AccountOptionCode") == "BU_NAME" else value
                if (receipt.get("resolverId") != resolver or receipt.get("targetKey") != target
                        or receipt.get("canonicalValue") != expected_value or receipt.get("matchCount") != 1
                        or (resolver != "RESOLVER-MPS-BU" and receipt.get("enabledAndEffective") is not True)
                        or receipt.get("baselineSha256") != getattr(baseline, "archive_sha256", None)
                        or not receipt.get("baselineSha256") or not receipt.get("evidenceRef")):
                    raise ValueError("MPS-RESOLVER: Evidence must bind this option, value, target and current baseline.")
        if op.get("entity") == DEFINITION and op.get("action") == "update":
            key = (target.get(PARENT), target.get("AccountOptionCode"))
            old = before.get(key, {})
            if any(field in values and values[field] != old.get(field)
                   for field in ("SecuredFlag", "TopologyMgrCode")):
                raise ValueError("MPS-CLASSIFICATION: Change sensitivity or topology through Payments UI; do not reclassify during import.")


def candidate_issues(candidate, baseline, blueprint):
    policy = load()
    before, effective = definitions(baseline, blueprint.get("operations", []))
    unsafe = False
    for name, rows in candidate.rows.items():
        for row in rows:
            unsafe |= any(suspicious(v) or WITHHELD in str(v) for v in row.values())
            if name == ROOT:
                unsafe |= any(row.get(field) != "" for field in policy["rootCredentialFields"])
            if name == VALUE:
                value = row.get("AccountOptionValue", "")
                import_resolved_bu = row.get("AccountOptionCode") == "BU_NAME" and bool(row.get("BuName", "").strip())
                unsafe |= (blocked(policy, (row.get(PARENT), row.get("AccountOptionCode")), before, effective)
                           or (not str(value).strip() and not import_resolved_bu) or set(str(value)) == {"*"})
    return ([{"code": "MPS_SENSITIVE_CANDIDATE", "message": "Prohibited credential, unknown, blank or masked value row detected; values withheld."}]
            if unsafe else [])


def safe_report(report, requirements):
    result = copy.deepcopy(report)
    ids = {row["id"] for row in requirements if row.get("entity") == VALUE}
    for row in result.get("requirementMatrix", []):
        if row.get("requirementId") in ids:
            for key in ("requested", "candidate", "persisted"):
                row[key] = "[value comparison withheld]"
            row.pop("rawDifferences", None)
            row.pop("semanticEquivalences", None)
    return result
