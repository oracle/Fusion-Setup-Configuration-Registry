"""GL account-combination approval and receipt controls for Common Options.

The installed core OAuth and byte client owns authentication and HTTP behavior.
This adapter binds the GL request, approval and receipt and submits once.
"""
from __future__ import annotations

from argparse import Namespace
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable
import urllib.parse
from xml.etree import ElementTree

CORE_ROOT = Path(__file__).resolve().parents[6] / "core"
DEFAULT_PROPERTIES_PATH = CORE_ROOT / "auth" / "fusionEnv.properties"
SOAP_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
GL_NAMESPACE = "http://xmlns.oracle.com/apps/financials/generalLedger/accounts/codeCombinations/accountCombinationService/"
GL_TYPES_NAMESPACE = GL_NAMESPACE + "types/"
sys.path.insert(0, str(CORE_ROOT / "auth" / "fusion-oauth-authentication" / "scripts"))
sys.path.insert(0, str(CORE_ROOT / "fusion-api" / "ucm-rest-client" / "scripts"))
import ucm_rest_client as CORE_HTTP  # noqa: E402
from fusion_auth import read_properties, require_props, token_cache_path  # noqa: E402


class AccountCombinationError(RuntimeError):
    def __init__(self, failure_class: str, message: str, *, http_status: int | None = None,
                 may_have_applied: bool | None = None):
        super().__init__(message)
        self.failure_class = failure_class
        self.http_status = http_status
        self.may_have_applied = bool(may_have_applied)
        self.submission_state_known = may_have_applied is not None


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode("utf-8")).hexdigest()


def load_environment(properties: Path) -> dict[str, str]:
    try:
        props = read_properties(properties)
        require_props(props, ["environment", "restBaseUrl", "scope"])
        return props
    except (OSError, ValueError) as exc:
        raise AccountCombinationError("input_validation", "Cannot read a valid Fusion properties file.") from exc


def _validate_gl_payload(envelope: bytes, read_only: bool, context: dict[str, Any]) -> None:
    """Bind execution classification and business identity to the actual XML."""
    failure = "GL XML, read-only classification and ledger/segment context must agree."
    expected_mode = "No" if read_only else "Yes"
    ledger = context.get("ledgerName")
    segments = context.get("segments")
    if (set(context) != {"ledgerName", "segments", "dynamicInsertion"}
            or not isinstance(ledger, str) or not ledger.strip() or ledger != ledger.strip()
            or not isinstance(segments, list) or not 1 <= len(segments) <= 30
            or any(not isinstance(s, str) or not s.strip() for s in segments)
            or context.get("dynamicInsertion") != expected_mode
            or not isinstance(envelope, bytes) or len(envelope) > 1024 * 1024
            or b"\x00" in envelope or b"<!DOCTYPE" in envelope.upper()
            or b"<!ENTITY" in envelope.upper()):
        raise AccountCombinationError("input_validation", failure)
    try:
        root = ElementTree.fromstring(envelope)
        current = root
        for tag in (f"{{{SOAP_NAMESPACE}}}Envelope", f"{{{SOAP_NAMESPACE}}}Body",
                    f"{{{GL_TYPES_NAMESPACE}}}validateAndCreateAccounts",
                    f"{{{GL_TYPES_NAMESPACE}}}validationInputRowList"):
            if (current.tag != tag or current.attrib or (current.text or "").strip()
                    or (current.tail or "").strip()):
                raise ValueError("Unexpected SOAP structure.")
            if tag.endswith("validationInputRowList"):
                break
            if len(current) != 1:
                raise ValueError("Expected exactly one GL operation and row.")
            current = current[0]
        names = ["DynamicInsertion", *[f"Segment{i}" for i in range(1, len(segments) + 1)], "LedgerName"]
        expected = [(f"{{{GL_NAMESPACE}}}{name}", value)
                    for name, value in zip(names, [expected_mode, *segments, ledger], strict=True)]
        actual = [(node.tag, node.text or "") for node in current]
        if actual != expected or any(len(node) or node.attrib or (node.tail or "").strip() for node in current):
            raise ValueError("Unexpected GL fields or values.")
    except (ElementTree.ParseError, LookupError, ValueError) as exc:
        raise AccountCombinationError("input_validation", failure) from exc


def request_context(props: dict[str, str], *, endpoint: str, soap_action: str,
                    operation: str, envelope: bytes, read_only: bool,
                    business_context: dict[str, Any]) -> dict[str, Any]:
    expected_action = ("http://xmlns.oracle.com/apps/financials/generalLedger/accounts/"
                       "codeCombinations/accountCombinationService/validateAndCreateAccounts")
    if (endpoint != "/fscmService/AccountCombinationService" or soap_action != expected_action
            or operation != "validateAndCreateAccounts"):
        raise AccountCombinationError("input_validation", "Only the declared GL account-combination operation is supported.")
    try:
        require_props(props, ["environment", "restBaseUrl", "scope"])
        if any(not props[name].strip() for name in ("environment", "restBaseUrl", "scope")):
            raise ValueError("Blank environment identity.")
    except (ValueError, AttributeError) as exc:
        raise AccountCombinationError("input_validation", "Environment identity, HTTPS origin and OAuth scope are required.") from exc
    base = props["restBaseUrl"].rstrip("/")
    parsed = urllib.parse.urlsplit(base)
    try:
        parsed.port
    except ValueError as exc:
        raise AccountCombinationError("input_validation", "Invalid Fusion origin port.") from exc
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path or any(c.isspace() for c in base)):
        raise AccountCombinationError("input_validation", "Fusion base URL must be an HTTPS origin.")
    if (not endpoint.startswith("/") or endpoint.startswith("//")
            or any(c in endpoint for c in "?#\\") or any(c.isspace() or ord(c) < 32 for c in endpoint)
            or ".." in endpoint.split("/")):
        raise AccountCombinationError("input_validation", "SOAP endpoint must be a path on the selected origin.")
    if (not soap_action.strip() or not soap_action.isascii()
            or any(ord(c) < 32 for c in soap_action) or not operation.strip()):
        raise AccountCombinationError("input_validation", "SOAPAction and operation are required.")
    if type(read_only) is not bool or not isinstance(business_context, dict):
        raise AccountCombinationError("input_validation", "Explicit read-only classification and business context required.")
    _validate_gl_payload(envelope, read_only, business_context)
    try:
        ElementTree.fromstring(envelope)
        # Detach mutable consumer state; only JSON-safe context can enter the record.
        context = json.loads(json.dumps(business_context, allow_nan=False))
    except (ElementTree.ParseError, TypeError, ValueError) as exc:
        raise AccountCombinationError("input_validation", "Invalid SOAP XML or business context.") from exc
    return {"environment": props["environment"], "baseUrl": base,
            "endpointPath": endpoint, "soapAction": soap_action, "operation": operation,
            "readOnly": read_only, "payloadSha256": hashlib.sha256(envelope).hexdigest(),
            "businessContext": context}


def approval_reference(approval: dict[str, Any] | None, request: dict[str, Any]) -> dict[str, str] | None:
    if request["readOnly"]:
        return None
    try:
        matches = isinstance(approval, dict) and digest(approval.get("request")) == digest(request)
    except (ValueError, TypeError):
        matches = False
    if (not isinstance(approval, dict) or approval.get("schemaVersion") != "fscr-soap-approval-v1"
            or approval.get("approved") is not True
            or not isinstance(approval.get("approvalId"), str) or not approval["approvalId"].strip()
            or not matches):
        raise AccountCombinationError("approval_blocker", "Approval must match the complete current SOAP request context.")
    return {"approvalId": approval["approvalId"], "approvalRecordSha256": digest(approval)}


def _checked_path(path: Path) -> Path:
    path = Path(os.path.abspath(path.expanduser()))
    for part in [*reversed(path.parents), path]:
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise AccountCombinationError("input_validation", "Linked receipt paths are not permitted.")
    return path


class NewJsonReceipt:
    """Reserve before calls; preserve checkpoints if later persistence fails."""
    def __init__(self, path: Path, protected_inputs: list[Path]):
        self.path = _checked_path(path)
        if any(self.path == p.expanduser().resolve() for p in protected_inputs):
            raise AccountCombinationError("input_validation", "Receipt destination overlaps an input.")
        self.identity: tuple[int, int] | None = None

    def __enter__(self):
        try:
            if self.path.exists():
                raise AccountCombinationError("input_validation", "Receipt destination already exists.")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            _checked_path(self.path)
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write('{"status":"RESERVED"}\n')
                stream.flush()
                os.fsync(stream.fileno())
                stat = os.fstat(stream.fileno())
                self.identity = (stat.st_dev, stat.st_ino)
            return self
        except OSError as exc:
            raise AccountCombinationError("artifact_persistence", "Cannot reserve a new receipt destination.") from exc

    def write(self, value: dict[str, Any]) -> None:
        staging = None
        try:
            rendered = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
            _checked_path(self.path)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".account-combination-receipt-", delete=False) as stream:
                staging = Path(stream.name)
                stream.write(rendered)
                stream.flush()
                os.fsync(stream.fileno())
            current = self.path.stat(follow_symlinks=False)
            if (current.st_dev, current.st_ino) != self.identity:
                raise AccountCombinationError("artifact_persistence", "Reserved receipt was replaced; refusing overwrite.")
            os.replace(staging, self.path)
            stat = self.path.stat(follow_symlinks=False)
            self.identity = (stat.st_dev, stat.st_ino)
        except (OSError, ValueError, TypeError) as exc:
            raise AccountCombinationError("artifact_persistence", "Cannot persist receipt; retain the prior checkpoint.") from exc
        finally:
            if staging is not None:
                try:
                    staging.unlink(missing_ok=True)
                except OSError:
                    pass  # Preserve the primary persistence diagnostic.

    def __exit__(self, *args):
        # Never remove execution evidence, even when authentication or submission fails.
        return False


def write_new_json(path: Path, value: dict[str, Any], *, protected_inputs: list[Path]) -> None:
    with NewJsonReceipt(path, protected_inputs) as receipt:
        receipt.write(value)


def _request_bytes(*, url: str, soap_action: str, envelope: bytes,
                  timeout: int, props: dict[str, str],
                  options: Namespace,
                  before_dispatch=None) -> tuple[bytes, int]:
    """Use the installed core client once; retain only task-safe failures."""
    try:
        authorization = CORE_HTTP.get_authorization_header(props, options)
    except (CORE_HTTP.FusionHttpError, OSError, RuntimeError, ValueError) as exc:
        raise AccountCombinationError(
            "auth_or_authz", "Core OAuth authorization failed; details omitted.",
            http_status=getattr(exc, "status_code", None),
            may_have_applied=False) from exc
    if before_dispatch is not None:
        before_dispatch()
    try:
        content, _headers, status = CORE_HTTP.request_bytes(
            props, url, method="POST", authorization=authorization, body=envelope,
            headers={"Accept": "text/xml, application/soap+xml",
                     "Content-Type": "text/xml; charset=UTF-8", "SOAPAction": soap_action},
            timeout=timeout)
        return content, status
    except CORE_HTTP.FusionHttpError as exc:
        failure_class = "auth_or_authz" if exc.status_code in {401, 403} else "fusion_api"
        raise AccountCombinationError(
            failure_class, "GL SOAP request failed; response content omitted.",
            http_status=exc.status_code) from exc
    except (OSError, RuntimeError, ValueError) as exc:
        raise AccountCombinationError(
            "transport_or_environment", "Core could not complete the GL SOAP request; details omitted.") from exc


def execute(props: dict[str, str], *, endpoint: str, soap_action: str, operation: str,
            envelope: bytes, read_only: bool, business_context: dict[str, Any],
            summarize: Callable[..., dict[str, Any]], output: Path | None = None,
            approval: dict[str, Any] | None = None, protected_inputs: list[Path] | None = None,
            token_cache: str | None = None, force_login: bool = False, open_browser: bool = True,
            timeout: int = 60, callback_timeout: int = 60) -> dict[str, Any]:
    if timeout <= 0 or callback_timeout <= 0:
        raise AccountCombinationError("input_validation", "Timeouts must be positive.")
    request = request_context(props, endpoint=endpoint, soap_action=soap_action, operation=operation,
                              envelope=envelope, read_only=read_only, business_context=business_context)
    approved = approval_reference(approval, request)
    if not read_only and output is None:
        raise AccountCombinationError("input_validation", "Mutation requires a new receipt destination.")
    inputs = list(protected_inputs or []) + [token_cache_path(props, token_cache)]
    reservation = NewJsonReceipt(output, inputs) if output else nullcontext(None)
    started = False
    evidence = {"schemaVersion": "fscr-soap-receipt-v1", "request": request, "approval": approved}
    with reservation as receipt:
        def checkpoint(status: str, **details: Any) -> None:
            if receipt:
                receipt.write({**evidence, "status": status, **details})
        try:
            checkpoint("PREPARED", mayHaveApplied=False)
            options = Namespace(auth_mode="oauth", access_token=None, redirect_url=None,
                                auth_code=None, open_browser=open_browser,
                                callback_timeout=callback_timeout, token_cache=token_cache,
                                force_login=force_login, timeout=timeout)
            def before_dispatch() -> None:
                nonlocal started
                checkpoint("REQUEST_STARTED", mayHaveApplied=not read_only)
                started = True
            content, status = _request_bytes(
                url=request["baseUrl"] + endpoint, soap_action=soap_action, envelope=envelope,
                timeout=timeout, props=props, options=options,
                before_dispatch=before_dispatch)
            try:
                summary = summarize(content, http_status=status)
                if not isinstance(summary, dict):
                    raise ValueError("Response summary must be an object.")
            except (RuntimeError, ValueError) as exc:
                raise AccountCombinationError("fusion_api", "SOAP result could not be interpreted; reconcile the request.") from exc
            result = {**summary, **evidence, "status": "RESPONSE_RECEIVED", "mayHaveApplied": not read_only,
                      "observedAt": datetime.now(timezone.utc).isoformat()}
            if receipt:
                receipt.write(result)
            return result
        except AccountCombinationError as exc:
            if not exc.submission_state_known:
                exc.may_have_applied = started and not read_only
            if exc.failure_class != "artifact_persistence":
                try:
                    checkpoint("FAILED", failureClass=exc.failure_class, httpStatus=exc.http_status,
                               mayHaveApplied=exc.may_have_applied, message=str(exc))
                except AccountCombinationError:
                    raise AccountCombinationError("artifact_persistence", "Failure receipt could not be saved; retain the checkpoint and reconcile.",
                                          may_have_applied=exc.may_have_applied) from exc
            raise
