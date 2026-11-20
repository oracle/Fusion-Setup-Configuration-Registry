#!/usr/bin/env python3
"""Bind this task's descriptor to its bundled offline FSM package primitives."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

TASK_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = TASK_ROOT / "e2e-adapter.json"
RUNTIME_PATH = "scripts/fsm_package_primitives.py"


def _load_runtime():
    descriptor = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(descriptor, dict) or not isinstance(descriptor.get("runtimeDependencies"), dict):
        raise ValueError("Task descriptor must declare an object of task-local runtime dependencies.")
    expected = descriptor["runtimeDependencies"].get(RUNTIME_PATH)
    path = TASK_ROOT / RUNTIME_PATH
    if not isinstance(expected, str) or not path.is_file() or path.is_symlink():
        raise ValueError("The declared task-local FSM runtime is unavailable; restore the task's bundled primitives.")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError("The task-local FSM runtime differs from the reviewed task binding; revalidate and refresh the dependency binding.")
    spec = importlib.util.spec_from_file_location("_fscr_ppr_fsm_package_runtime", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the declared task-local FSM runtime.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


try:
    runtime = _load_runtime()
except (OSError, ValueError) as exc:
    diagnostic = {"failure_class": "catalog_or_metadata_mismatch", "stage": "load_runtime_dependency",
                  "recommended_action": "Restore the task's bundled primitives and rerun local validation."}
    print(json.dumps({"status": "FAIL", **diagnostic,
                      "errors": [{"code": "RUNTIME_DEPENDENCY", "message": str(exc), **diagnostic}]}), file=sys.stderr)
    raise SystemExit(2)

# Preserve the runtime callable interface and dependency-injection surface. This
# loader creates a separate module instance; the task hook below never changes
# another task's runtime or the bundled base primitives.
globals().update({name: getattr(runtime, name) for name in dir(runtime) if not name.startswith("__")})

_PPR_ROOT_ENTITY = "ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES"
_PPR_PARENT_FIELD = "ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName"
_PPR_SELECTION_ENTITIES = (
    "ORA_PPR_BU_GROUP", "ORA_PPR_CURRENCY_GROUP", "ORA_PPR_LE_GROUP",
    "ORA_PPR_PAY_GROUP", "ORA_PPR_SOURCE_GROUP",
)
_ppr_core_reconcile = runtime.reconcile
_ppr_core_validate_blueprint = runtime._validate_blueprint
_ppr_core_candidate_rows = runtime._candidate_rows
_ppr_core_semantic_issues = runtime._semantic_issues
_ppr_core_normalize_design = runtime.normalize_design
_ppr_core_validate_candidate = runtime.validate_candidate


def _validate_blueprint(contract, blueprint, baseline=None):
    """Keep preservation mandatory for this task's bounded operations."""
    _ppr_core_validate_blueprint(contract, blueprint, baseline)
    for operation in blueprint["operations"]:
        for flag in ("preserveOtherValues", "preserveUnspecifiedRows"):
            if operation.get(flag, True) is not True:
                raise AdapterError(
                    "PPR bounded operations require full value and row preservation; "
                    + flag + " must be true."
                )
    if baseline is not None:
        _parent_context_rows(contract, baseline, blueprint)


# Runtime preparation/comparison functions resolve this hook in their own
# isolated module, so hand-edited blueprints cannot bypass it through the CLI.
runtime._validate_blueprint = _validate_blueprint


def _parent_context_rows(contract, baseline, blueprint):
    """Retain each existing parent needed by an otherwise child-only create."""
    root = _entity_map(contract)[_PPR_ROOT_ENTITY]
    explicit = {
        _target_tuple(root, operation["targetKey"])
        for operation in blueprint["operations"]
        if operation["entity"] == _PPR_ROOT_ENTITY
    }
    required = {
        (str(operation["targetKey"][_PPR_PARENT_FIELD]),)
        for operation in blueprint["operations"]
        if operation["entity"] in _PPR_SELECTION_ENTITIES
        and operation["action"] == "create"
    } - explicit
    parents = _row_index(baseline, root)
    rows = []
    for key in sorted(required):
        if key not in parents:
            raise AdapterError(f"PPR child create requires an exact retained parent {key!r}.")
        row = dict(parents[key])
        if not row["PaymentConversionRateType"].strip():
            raise AdapterError(
                f"Parent context {key!r} has a blank required PaymentConversionRateType; "
                "request an explicit supported root correction instead of inventing a default."
            )
        for field in root["auditFields"]:
            row[field] = ""
        rows.append(row)
    return rows


def _parent_context_preview(contract, baseline, blueprint):
    root = _entity_map(contract)[_PPR_ROOT_ENTITY]
    return [{
        "entity": _PPR_ROOT_ENTITY,
        "targetKey": {"TemplateName": row["TemplateName"]},
        "values": {field: row[field] for field in root["headers"]
                   if field not in root["auditFields"]},
        "role": "Unchanged parent context for child membership creation; not a new root operation.",
    } for row in _parent_context_rows(contract, baseline, blueprint)]


def _candidate_rows(contract, baseline, blueprint):
    rows = _ppr_core_candidate_rows(contract, baseline, blueprint)
    rows[_PPR_ROOT_ENTITY].extend(_parent_context_rows(contract, baseline, blueprint))
    root = _entity_map(contract)[_PPR_ROOT_ENTITY]
    rows[_PPR_ROOT_ENTITY].sort(key=lambda row: _row_key(root, row))
    return rows


def _semantic_issues(contract, candidate, baseline, blueprint, requirements):
    """Validate retained context separately without authorizing other rows."""
    root = _entity_map(contract)[_PPR_ROOT_ENTITY]
    expected = {_row_key(root, row): row
                for row in _parent_context_rows(contract, baseline, blueprint)}
    actual = _row_index(candidate, root)
    operation_candidate = deepcopy(candidate)
    operation_candidate.rows[_PPR_ROOT_ENTITY] = [
        row for row in candidate.rows[_PPR_ROOT_ENTITY]
        if _row_key(root, row) not in expected
    ]
    issues = _ppr_core_semantic_issues(
        contract, operation_candidate, baseline, blueprint, requirements
    )
    for key, retained in expected.items():
        row = actual.get(key)
        if row is None:
            issues.append({"code": "PPR_MISSING_PARENT_CONTEXT",
                           "message": f"Candidate lacks the retained parent context {key!r}."})
            continue
        for field in root["headers"]:
            if row[field] != retained[field]:
                issues.append({"code": "PPR_PARENT_CONTEXT_MISMATCH", "message":
                               f"Parent context {key!r} must preserve baseline {field}; audit cells must be blank."})
    return issues


def normalize_design(contract, baseline_path, request_path, design_path):
    blueprint, preview, requirements = _ppr_core_normalize_design(
        contract, baseline_path, request_path, design_path
    )
    preview["parentContextRows"] = _parent_context_preview(
        contract, _read_package(baseline_path, contract), blueprint
    )
    return blueprint, preview, requirements


def validate_candidate(contract, template_path, baseline_path, blueprint_path, requirements_path, candidate_path):
    result = _ppr_core_validate_candidate(
        contract, template_path, baseline_path, blueprint_path, requirements_path, candidate_path
    )
    result["parentContextRows"] = _parent_context_preview(
        contract, _read_package(baseline_path, contract), _read_json(blueprint_path)
    )
    return result


runtime._candidate_rows = _candidate_rows
runtime._semantic_issues = _semantic_issues
runtime.normalize_design = normalize_design
runtime.validate_candidate = validate_candidate


def reconcile(contract, baseline_path, candidate_path, blueprint_path, requirements_path, export_path):
    """Compare all affected PPR selection sets without asserting persistence."""
    result = _ppr_core_reconcile(
        contract, baseline_path, candidate_path, blueprint_path, requirements_path, export_path
    )
    # The runtime validates the blueprint, requirements and comparison-source identity
    # before this task-specific check. Candidate validation remains a separate
    # required workflow step; candidate rows alone never authorize membership.
    entities = _entity_map(contract)
    if not {_PPR_ROOT_ENTITY, *_PPR_SELECTION_ENTITIES} <= set(entities):
        raise AdapterError("PPR reconciliation requires the root and all five selection collections.")
    baseline = _read_package(baseline_path, contract)
    persisted = _read_package(export_path, contract)
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    affected = set()
    for operation in blueprint["operations"]:
        parent_field = "TemplateName" if operation["entity"] == _PPR_ROOT_ENTITY else _PPR_PARENT_FIELD
        affected.add(str(operation["targetKey"][parent_field]))

    requested_rows = _candidate_rows(contract, baseline, blueprint)
    effects = _source_effects(contract, blueprint)
    checks = []
    for entity_name in _PPR_SELECTION_ENTITIES:
        entity = entities[entity_name]
        expected = dict(_row_index(baseline, entity))
        expected.update({_row_key(entity, row): row for row in requested_rows[entity_name]})
        # Only a declared setter effect can remove existing members. Empty or
        # omitted candidate CSVs do not describe deletion or replacement.
        for effect in effects:
            if effect["kind"] == "remove-child-rows" and effect["childEntity"] == entity_name:
                expected = {key: row for key, row in expected.items() if not _effect_matches_row(effect, row)}
        observed = _row_index(persisted, entity)
        for parent in sorted(affected):
            expected_keys = {key for key, row in expected.items() if row[_PPR_PARENT_FIELD] == parent}
            observed_keys = {key for key, row in observed.items() if row[_PPR_PARENT_FIELD] == parent}
            encode_keys = lambda keys: [dict(zip(entity["keyFields"], key)) for key in sorted(keys)]
            checks.append({
                "requirementId": f"PPR.EXACT_CHILD_MEMBERSHIP:{entity_name}:{parent}",
                "kind": "exact_child_membership",
                "requirement": f"Exact {entity_name} membership for template {parent}.",
                "entity": entity_name,
                "targetKey": {"TemplateName": parent},
                "requested": {"count": len(expected_keys), "keys": encode_keys(expected_keys)},
                "persisted": {"count": len(observed_keys), "keys": encode_keys(observed_keys)},
                "missingKeys": encode_keys(expected_keys - observed_keys),
                "unexpectedKeys": encode_keys(observed_keys - expected_keys),
                "passed": expected_keys == observed_keys,
                "detail": "Expected membership derives from the full baseline, validated requested operations, and declared source effects.",
            })
    result["requirementMatrix"].extend(checks)
    result["mismatchCount"] = sum(not row["passed"] for row in result["requirementMatrix"])
    result["comparisonStatus"] = "FAIL" if result["mismatchCount"] else "PASS"
    result["status"] = "FAIL" if result["mismatchCount"] else "COMPARISON_ONLY"
    result["persistenceVerified"] = False
    return result


# The runtime's CLI dispatch resolves reconcile in this isolated module namespace.
# Installing the same hook here keeps CLI and direct task calls equivalent.
runtime.reconcile = reconcile


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] not in {"-h", "--help"} and not any(arg == "--contract" or arg.startswith("--contract=") for arg in arguments):
        arguments.extend(["--contract", str(CONTRACT_PATH)])
    parsed = runtime.parse_args(arguments)
    if parsed.contract.resolve() != CONTRACT_PATH.resolve():
        diagnostic = {"failure_class": "input_validation", "stage": "bind_task_contract",
                      "recommended_action": "Use this task's bundled descriptor; route a different task through its owning skill."}
        print(json.dumps({"status": "FAIL", **diagnostic, "errors": [{
            "code": "TASK_CONTRACT_MISMATCH", "message": "This task entrypoint cannot use another descriptor.",
            **diagnostic}]}), file=sys.stderr)
        return 2
    return runtime.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
