#!/usr/bin/env python3
"""Run the shared Invoice Options read-only preflight for Payment Options.

Payment Options and Invoice Options mutate the same AP_SYSTEM_PARAMETER row.
The owner adapter stays offline, while this wrapper delegates a live, read-only
preflight to the sibling task's established resolver before normalization.
That resolver calls only the APIs applicable to the supplied operation and
values; it never performs a Fusion write.

This wrapper intentionally has no Payment Options lookup logic of its own. It
forwards the Invoice Options preflight so the two tasks cannot drift apart.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


TASK_ROOT = Path(__file__).resolve().parents[1]
INVOICE_TASK_ROOT = TASK_ROOT.parent / "manage-invoice-options"
INVOICE_ADAPTER = INVOICE_TASK_ROOT / "scripts" / "fsm_task_adapter.py"
INVOICE_RESOLVER = INVOICE_TASK_ROOT / "scripts" / "resolve_lookup_prerequisites.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load delegated Invoice Options module {path}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_delegate():
    if not INVOICE_ADAPTER.is_file() or not INVOICE_RESOLVER.is_file():
        raise RuntimeError(
            "Manage Payment Options requires the sibling Manage Invoice Options "
            "adapter and lookup preflight runtime."
        )
    # The sibling resolver imports ``fsm_task_adapter`` by this conventional
    # name.  Register its own module first so this wrapper never binds the
    # Payment Options adapter by mistake.
    _load_module("fsm_task_adapter", INVOICE_ADAPTER)
    return _load_module("invoice_options_lookup_preflight", INVOICE_RESOLVER)


DELEGATE = _load_delegate()
INVOICE_OWNED_PAYMENT_TERM_FIELDS = frozenset(
    {"TermName", "PrepaymentTermName", "EmployeeTermName"}
)


def _without_invoice_owned_payment_term_fields(design: dict[str, Any]) -> dict[str, Any]:
    """Keep required create TermName for its owning read-only resolver.

    A new shared row needs its supplied TermName receipt. Other Invoice-owned
    term fields and all update term changes remain outside Payment ownership.
    """
    preflight_design = copy.deepcopy(design)
    operations = preflight_design.get("operations")
    if not isinstance(operations, list):
        return preflight_design
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        values = operation.get("values")
        if not isinstance(values, dict):
            continue
        shared_create = (
            operation.get("action") == "create"
            and operation.get("entity") == "AP_SYSTEM_PARAMETER"
        )
        for field in INVOICE_OWNED_PAYMENT_TERM_FIELDS:
            if shared_create and field == "TermName":
                continue
            values.pop(field, None)
    return preflight_design


def main(argv: list[str] | None = None) -> int:
    """Delegate required create references; preserve update ownership limits."""
    args = DELEGATE.parse_args(argv)
    try:
        DELEGATE._validate_new_outputs([args.output], [value for key, value in vars(args).items()
                                                     if key != "output" and isinstance(value, Path)])
        design = DELEGATE._read_json(args.design)
        config = DELEGATE.metadata.read_config(
            args.properties, **DELEGATE.metadata.oauth_kwargs(args)
        )
        if args.reference_context:
            config["referenceContext"] = DELEGATE._read_json(args.reference_context)
        baseline = (DELEGATE._read_package(args.baseline, DELEGATE._load_contract(TASK_ROOT / "e2e-adapter.json"))
                    if args.baseline else None)
        resolved, summary = DELEGATE.resolve_lookup_prerequisites(
            _without_invoice_owned_payment_term_fields(design), config, baseline
        )
        # The delegate does not transform operation values. Restore the original
        # operations so the output remains a faithful Payment Options design.
        resolved["operations"] = design.get("operations")
        DELEGATE._write_json(args.output, resolved)
        print(json.dumps({"status": "PASS", **summary, "output": str(args.output)}, sort_keys=True))
        return 0
    except (DELEGATE.AdapterError, DELEGATE.LookupPreflightError, DELEGATE.metadata.DataLoadError, OSError) as exc:
        failure = {"status": "FAIL", "error": str(exc)}
        if hasattr(exc, "classification"):
            failure.update(classification=exc.classification, failureClass=exc.failure_class)
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
