#!/usr/bin/env python3
"""Internal OAuth transport for governed Oracle CPQ REST capabilities.

The transport owns HTTPS, OAuth, response parsing, and safe error details. It
does not decide which CPQ endpoint or payload a task may use. Callers must
enforce those allowlists before invoking the one-shot mutation primitive.
GET may refresh authentication once after 401/403; PATCH is never retried.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "core" / "auth" / "fusion-oauth-authentication" / "scripts").is_dir():
            return candidate
    raise RuntimeError("Could not locate the FSCR repository root.")


CORE_ROOT = _find_repo_root(Path(__file__).resolve())
AUTH_SCRIPTS_PATH = CORE_ROOT / "core" / "auth" / "fusion-oauth-authentication" / "scripts"
sys.path.insert(0, str(AUTH_SCRIPTS_PATH))

from fusion_auth import (  # noqa: E402
    DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    get_access_token,
    read_properties,
    require_props,
)


SAFE_DIAGNOSTIC_HEADERS = frozenset(
    {
        "x-oracle-dms-ecid",
        "x-request-id",
        "request-id",
        "opc-request-id",
    }
)


# CPQ may return a useful, operator-facing business explanation for an HTTP
# failure.  Keep that benefit without turning the error path into a response
# body/logging channel.  Only a small, allowlisted JSON subset is considered,
# it is bounded before JSON parsing, and anything that looks credential-like
# is discarded rather than reported.
_MAX_PROVIDER_ERROR_BODY_BYTES = 16 * 1024
_MAX_PROVIDER_ERROR_MESSAGE_CHARS = 600
_MAX_PROVIDER_ERROR_CODE_CHARS = 128
_MAX_DIAGNOSTIC_ID_CHARS = 256
_MAX_SUCCESS_RESPONSE_BODY_BYTES = 16 * 1024 * 1024
_SAFE_PROVIDER_MESSAGE_KEYS = (
    "Error",
    "message",
    "Message",
    "error_description",
    "errorDescription",
    "title",
    "detail",
    "error",
)
_SAFE_PROVIDER_CODE_KEYS = ("errorCode", "error_code", "code")
_SENSITIVE_PROVIDER_TEXT = re.compile(
    r"\b(?:access[_ -]?token|refresh[_ -]?token|id[_ -]?token|token|secret|password|authorization|bearer|basic|client[_ -]?id)\b",
    re.IGNORECASE,
)
_SAFE_PROVIDER_CODE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}\Z")
_SAFE_DIAGNOSTIC_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/;+=,@-]{0,255}\Z")


class CpqClientError(RuntimeError):
    """Base class for safe CPQ transport failures."""


class CpqConfigurationError(CpqClientError):
    """Raised before an HTTP request when CPQ configuration is unsafe or incomplete."""


class CpqResponseError(CpqClientError):
    """Raised when a CPQ response does not match the expected JSON contract."""


class CpqTransportError(CpqClientError):
    """Raised for CPQ connectivity failures before a response is available."""


class CpqHttpError(CpqClientError):
    """A safe HTTP failure that never exposes a raw CPQ response body."""

    def __init__(
        self,
        *,
        status_code: int,
        method: str,
        path: str,
        diagnostic_ids: Mapping[str, str],
        provider_message: str | None = None,
        provider_code: str | None = None,
    ) -> None:
        self.provider_message = _safe_provider_message(provider_message)
        self.provider_code = _safe_provider_code(provider_code)
        rendered = f"CPQ returned HTTP {status_code} for {method} {path}."
        details: list[str] = []
        if self.provider_message:
            details.append(f"Oracle CPQ message: {self.provider_message}")
        if self.provider_code and self.provider_code not in (self.provider_message or ""):
            details.append(f"Oracle CPQ code: {self.provider_code}")
        if details:
            rendered += " " + ". ".join(details) + "."
        super().__init__(rendered)
        self.status_code = status_code
        self.method = method
        self.path = path
        self.diagnostic_ids = dict(diagnostic_ids)


@dataclass(frozen=True)
class OAuthOptions:
    """OAuth options passed to the existing shared OAuth implementation."""

    redirect_url: str | None = None
    auth_code: str | None = None
    code_verifier: str | None = None
    open_browser: bool = True
    callback_timeout: int = DEFAULT_CALLBACK_TIMEOUT_SECONDS


@dataclass(frozen=True)
class CpqResponse:
    """Safe CPQ JSON response metadata exposed to an FDOS caller."""

    method: str
    path: str
    status: int
    payload: dict[str, Any]
    diagnostic_ids: dict[str, str]
    retry_count: int = 0

    def audit_summary(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "endpoint_path": self.path,
            "http_status": self.status,
            "retry_count": self.retry_count,
            "diagnostic_ids": self.diagnostic_ids,
        }


def validate_cpq_base_url(value: str) -> str:
    """Derive the external CPQ context root from canonical ``restBaseUrl``.

    The canonical REST client already defines ``restBaseUrl`` as the Fusion
    site root.  Programmatic CPQ consumers use that same property and append
    the fixed ``/cpq`` context; they do not introduce a second host setting.
    """

    parsed = urllib.parse.urlsplit(value.strip())
    try:
        port = parsed.port
    except ValueError as exc:
        raise CpqConfigurationError("restBaseUrl has an invalid port.") from exc
    if parsed.scheme != "https" or not parsed.hostname:
        raise CpqConfigurationError("restBaseUrl must be an HTTPS URL with a host.")
    if parsed.username or parsed.password:
        raise CpqConfigurationError("restBaseUrl must not contain credentials.")
    if parsed.query or parsed.fragment:
        raise CpqConfigurationError("restBaseUrl must not contain a query or fragment.")
    context_path = parsed.path.rstrip("/")
    if context_path:
        raise CpqConfigurationError(
            "restBaseUrl must be the Fusion site root without a path: https://<host>"
        )
    if port not in {None, 443}:
        raise CpqConfigurationError("restBaseUrl must use the default HTTPS port.")
    return urllib.parse.urlunsplit(("https", parsed.netloc, "/cpq", "", ""))


def build_cpq_oauth_properties(properties: Mapping[str, str]) -> dict[str, str]:
    """Adapt secure CPQ settings to the existing shared OAuth property contract."""

    fusion_base_url = properties.get("restBaseUrl", "").strip()
    cpq_scope = properties.get("cpq_scope", "").strip()
    if not fusion_base_url:
        raise CpqConfigurationError("Missing required CPQ property: restBaseUrl")
    if not cpq_scope:
        raise CpqConfigurationError("Missing required CPQ OAuth scope property: cpq_scope")

    scoped = dict(properties)
    # Validate that the canonical Fusion root can safely derive the CPQ
    # context, but preserve the canonical root for the shared OAuth contract.
    validate_cpq_base_url(fusion_base_url)
    scoped["restBaseUrl"] = fusion_base_url.rstrip("/")
    scoped["scope"] = cpq_scope
    try:
        require_props(
            scoped,
            [
                "environment",
                "restBaseUrl",
                "clientId",
                "scope",
                "redirectUrl",
                "tokenUrl",
                "authorizeUrl",
            ],
        )
    except ValueError as exc:
        raise CpqConfigurationError(str(exc)) from exc
    return scoped


def _safe_diagnostic_ids(headers: Mapping[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}
    diagnostic_ids: dict[str, str] = {}
    for key, value in headers.items():
        normalized_key = key.lower()
        if normalized_key not in SAFE_DIAGNOSTIC_HEADERS or not isinstance(value, str):
            continue
        normalized_value = value.strip()
        if (
            not normalized_value
            or len(normalized_value) > _MAX_DIAGNOSTIC_ID_CHARS
            or not _SAFE_DIAGNOSTIC_ID.fullmatch(normalized_value)
        ):
            continue
        diagnostic_ids[normalized_key] = normalized_value
    return diagnostic_ids


def _safe_provider_message(value: Any) -> str | None:
    """Return a bounded provider business message only when it is safe to show."""

    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized or _SENSITIVE_PROVIDER_TEXT.search(normalized):
        return None
    if len(normalized) > _MAX_PROVIDER_ERROR_MESSAGE_CHARS:
        normalized = normalized[:_MAX_PROVIDER_ERROR_MESSAGE_CHARS].rstrip() + "…"
    return normalized


def _safe_provider_code(value: Any) -> str | None:
    """Return a compact provider error identifier when it is safe to retain."""

    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if (
        not normalized
        or len(normalized) > _MAX_PROVIDER_ERROR_CODE_CHARS
        or _SENSITIVE_PROVIDER_TEXT.search(normalized)
        or not _SAFE_PROVIDER_CODE.fullmatch(normalized)
    ):
        return None
    return normalized


def _first_safe_provider_message(payload: Mapping[str, Any]) -> str | None:
    for key in _SAFE_PROVIDER_MESSAGE_KEYS:
        message = _safe_provider_message(payload.get(key))
        if message:
            return message
    return None


def _first_safe_provider_code(payload: Mapping[str, Any]) -> str | None:
    for key in _SAFE_PROVIDER_CODE_KEYS:
        code = _safe_provider_code(payload.get(key))
        if code:
            return code
    return None


def _safe_provider_error_details(error: urllib.error.HTTPError) -> tuple[str | None, str | None]:
    """Read a small allowlisted JSON error subset without retaining the body.

    A non-JSON response, malformed payload, oversized response, or sensitive
    field is intentionally treated as an opaque HTTP failure.  The caller
    keeps only the returned message/code values, never ``content`` itself.
    """

    try:
        content = error.read(_MAX_PROVIDER_ERROR_BODY_BYTES)
    except (OSError, TypeError, ValueError):
        return None, None
    if not isinstance(content, (bytes, bytearray)) or not content.strip():
        return None, None
    try:
        payload = json.loads(bytes(content).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if not isinstance(payload, Mapping):
        return None, None

    message = _first_safe_provider_message(payload)
    code = _first_safe_provider_code(payload)
    nested_error = payload.get("error")
    if isinstance(nested_error, Mapping):
        message = message or _first_safe_provider_message(nested_error)
        code = code or _first_safe_provider_code(nested_error)
    return message, code


class _RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects so a CPQ bearer token never crosses an origin boundary."""

    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: Any,
        status_code: int,
        message: str,
        headers: Mapping[str, str],
        new_url: str,
    ) -> urllib.request.Request:
        del new_url
        raise urllib.error.HTTPError(
            request.full_url,
            status_code,
            f"{message} - CPQ redirects are not allowed",
            headers,
            file_pointer,
        )


def _open_without_redirects(request: urllib.request.Request, *, timeout: int) -> Any:
    """Open one request with redirects disabled for bearer-token safety."""

    return urllib.request.build_opener(_RejectRedirectHandler()).open(
        request,
        timeout=timeout,
    )


def _decode_json_object(content: bytes, *, method: str, path: str) -> dict[str, Any]:
    if not content.strip():
        return {}
    try:
        parsed = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CpqResponseError(f"CPQ returned a non-JSON response for {method} {path}.") from exc
    if not isinstance(parsed, dict):
        raise CpqResponseError(f"CPQ returned a non-object JSON response for {method} {path}.")
    return parsed


def _validate_relative_cpq_v19_path(path: str) -> str:
    """Reject a path that could escape the configured CPQ context root."""

    if not isinstance(path, str) or not path.startswith("/rest/v19/"):
        raise CpqConfigurationError("CPQ transport requires a relative /rest/v19/ path.")
    if any(character in path for character in ("\\", "\x00", "\r", "\n")):
        raise CpqConfigurationError("CPQ endpoint path is malformed.")
    parsed = urllib.parse.urlsplit(path)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or parsed.path != path:
        raise CpqConfigurationError("CPQ endpoint path must not contain a host, query, or fragment.")
    if "//" in path or "/../" in path or path.endswith("/.."):
        raise CpqConfigurationError("CPQ endpoint path is malformed.")
    return path


class CpqOAuthTransport:
    """Private HTTPS/OAuth transport for caller-governed CPQ routes.

    Do not expose this class as a general user-facing REST client.  Its caller
    must validate endpoint/method/payload allowlists before using it.
    """

    def __init__(
        self,
        oauth_properties: Mapping[str, str],
        *,
        token_cache: str | None = None,
        timeout: int = 60,
        oauth_options: OAuthOptions | None = None,
        token_provider: Callable[..., str] = get_access_token,
        opener: Callable[..., Any] = _open_without_redirects,
    ) -> None:
        if not isinstance(timeout, int) or not 1 <= timeout <= 300:
            raise CpqConfigurationError("timeout must be an integer between 1 and 300 seconds.")
        self._oauth_properties = build_cpq_oauth_properties(oauth_properties)
        self._base_url = validate_cpq_base_url(self._oauth_properties["restBaseUrl"])
        self._token_cache = token_cache
        self._timeout = timeout
        self._oauth_options = oauth_options or OAuthOptions()
        self._token_provider = token_provider
        self._opener = opener
        self._cached_access_token: str | None = None

    @classmethod
    def from_properties_file(
        cls,
        properties_path: Path,
        *,
        token_cache: str | None = None,
        timeout: int = 60,
        oauth_options: OAuthOptions | None = None,
    ) -> "CpqOAuthTransport":
        try:
            properties = read_properties(properties_path)
        except (OSError, ValueError) as exc:
            # ``read_properties`` includes the malformed source line in its
            # ValueError.  A local profile may contain a secret on that line,
            # so never propagate that raw message into a CLI result.
            raise CpqConfigurationError("Unable to read the local CPQ OAuth properties file.") from exc
        return cls(
            properties,
            token_cache=token_cache,
            timeout=timeout,
            oauth_options=oauth_options,
        )

    @property
    def base_url(self) -> str:
        """Return the validated external CPQ context root for trusted callers."""

        return self._base_url

    def ensure_authenticated(self, *, force_login: bool = False) -> None:
        """Obtain an OAuth token without exposing it to a caller.

        Capability wrappers use this only when an operator explicitly requests
        a fresh login.  Returning ``None`` prevents an OAuth token from being
        copied into a task result, project artifact, or log.
        """

        self._access_token(force_login=force_login)

    def url_for_validated_path(self, path: str) -> str:
        """Build a URL for a path already validated by a public capability."""

        return self._url(path)

    def _access_token(self, *, force_login: bool = False) -> str:
        if self._cached_access_token and not force_login:
            return self._cached_access_token
        options = self._oauth_options
        token = self._token_provider(
            self._oauth_properties,
            redirect_url=options.redirect_url,
            auth_code=options.auth_code,
            code_verifier=options.code_verifier,
            open_browser=options.open_browser,
            callback_timeout=options.callback_timeout,
            token_cache=self._token_cache,
            force_login=force_login,
        )
        self._cached_access_token = token
        return token

    def _url(self, path: str) -> str:
        return f"{self._base_url}{_validate_relative_cpq_v19_path(path)}"

    def _send(
        self,
        *,
        method: str,
        path: str,
        json_body: dict[str, Any] | None,
        access_token: str,
        retry_count: int,
    ) -> CpqResponse:
        url = self._url(path)
        data = json.dumps(json_body).encode("utf-8") if json_body is not None else None
        headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self._opener(request, timeout=self._timeout) as response:
                content = response.read(_MAX_SUCCESS_RESPONSE_BODY_BYTES + 1)
                if len(content) > _MAX_SUCCESS_RESPONSE_BODY_BYTES:
                    raise CpqResponseError(
                        f"CPQ response exceeded the supported size for {method} {path}."
                    )
                response_headers = dict(response.headers.items())
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            diagnostic_ids = _safe_diagnostic_ids(dict(exc.headers.items()) if exc.headers else None)
            provider_message, provider_code = _safe_provider_error_details(exc)
            raise CpqHttpError(
                status_code=exc.code,
                method=method,
                path=path,
                diagnostic_ids=diagnostic_ids,
                provider_message=provider_message,
                provider_code=provider_code,
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise CpqTransportError(f"Unable to call CPQ {method} {path}.") from exc
        return CpqResponse(
            method=method,
            path=path,
            status=status,
            payload=_decode_json_object(content, method=method, path=path),
            diagnostic_ids=_safe_diagnostic_ids(response_headers),
            retry_count=retry_count,
        )

    def get_json(self, path: str) -> CpqResponse:
        """Run one safe GET, refreshing OAuth once only after 401/403."""

        try:
            return self._send(
                method="GET",
                path=path,
                json_body=None,
                access_token=self._access_token(),
                retry_count=0,
            )
        except CpqHttpError as exc:
            if exc.status_code not in {401, 403}:
                raise
            self._cached_access_token = None
            return self._send(
                method="GET",
                path=path,
                json_body=None,
                access_token=self._access_token(force_login=True),
                retry_count=1,
            )

    def _patch_json_once(self, *, path: str, json_body: Mapping[str, Any]) -> CpqResponse:
        """Send one caller-governed JSON PATCH without automatic retry.

        This low-level primitive is intentionally kept on the internal
        transport rather than the public read client. The calling capability
        must validate the exact endpoint and payload, bind them to a current
        approval, and handle an ambiguous outcome without retrying.
        """

        if not isinstance(json_body, Mapping):
            raise CpqConfigurationError("CPQ PATCH body must be a JSON object.")
        validated_path = _validate_relative_cpq_v19_path(path)
        return self._send(
            method="PATCH",
            path=validated_path,
            json_body=dict(json_body),
            access_token=self._access_token(),
            retry_count=0,
        )
