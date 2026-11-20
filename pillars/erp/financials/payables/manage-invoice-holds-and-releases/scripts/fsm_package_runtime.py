#!/usr/bin/env python3
"""Task-bound entrypoint for the local Invoice Holds package primitives."""

import importlib.util as _import_util
from pathlib import Path as _Path
import sys as _sys

_RUNTIME_PATH = _Path(__file__).resolve().with_name("fsm_package_primitives.py")
_RUNTIME_MODULE_NAME = "_payables_invoice_holds_package_primitives"
_package_runtime = _sys.modules.get(_RUNTIME_MODULE_NAME)
if _package_runtime is None:
    _spec = _import_util.spec_from_file_location(_RUNTIME_MODULE_NAME, _RUNTIME_PATH)
    if _spec is None or _spec.loader is None:
        raise ImportError("Cannot load the local Invoice Holds package primitives.")
    _package_runtime = _import_util.module_from_spec(_spec)
    _sys.modules[_RUNTIME_MODULE_NAME] = _package_runtime
    try:
        _spec.loader.exec_module(_package_runtime)
    except Exception:
        _sys.modules.pop(_RUNTIME_MODULE_NAME, None)
        raise

_package_runtime.bind_runtime(globals(), contract_path=_Path(__file__).resolve().parents[1] / "e2e-adapter.json")
bind_runtime = _package_runtime.bind_runtime
