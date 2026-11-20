"""Delegate to Core REST while preserving typed HTTP failures for FFS callers."""
from pathlib import Path
import json
import sys

CORE_SCRIPTS = Path(__file__).resolve().parents[4] / 'core/fusion-api/rest-api-client/scripts'
sys.path.insert(0, str(CORE_SCRIPTS))
from fusion_rest_client import main as run_core_client
from rest_client_common import FusionHttpError


def main() -> int:
    try:
        return run_core_client()
    except FusionHttpError as error:
        # Never parse error.body or echo its contents as transport status.
        print(json.dumps({'type': 'field_service_http_error', 'status': error.status_code}), file=sys.stderr)
        return 1
    except Exception as error:
        print(json.dumps({'type': 'field_service_client_error', 'exception': type(error).__name__}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
