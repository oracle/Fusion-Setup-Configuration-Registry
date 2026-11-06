#!/usr/bin/env python3
"""Read and validate current Oracle Fusion feature-state records.

This helper deliberately owns only the semantic ``featureStates`` read.  It
reuses the repository's standard Fusion REST transport for OAuth, URL building,
GET execution, and the one permitted 401/403 token-refresh retry.  It never
updates a feature, refreshes feature selections, or calls a CPQ endpoint.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


FEATURE_STATES_PATH = "/fscmRestApi/resources/latest/featureStates"
# The current-state lookup uses the advanced ADF ``q`` expression syntax
# (``FeatureMode='COMBO' AND FeatureCode IN (...)``).  Framework version 2
# is the first version that defines that syntax; without it, an environment
# can interpret the query using version 1 semantics and return an empty
# collection even though the requested feature records exist.
FEATURE_STATES_REST_FRAMEWORK_VERSION = "2"
DEFAULT_TOKEN_CACHE = "auto"
FEATURE_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
FEATURE_MODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

# An HTTP error body is untrusted.  The reader may surface a short business
# error only when it appears in one of these known JSON fields and contains no
# credential-like material or markup.  Never log, persist, or render the raw
# response body.
MAX_PROVIDER_ERROR_BODY_CHARS = 8_192
MAX_FEATURE_STATES_RESPONSE_BYTES = 1_048_576
MAX_PROVIDER_ERROR_MESSAGE_CHARS = 500
MAX_PROVIDER_ERROR_CODE_CHARS = 128
SAFE_PROVIDER_ERROR_MESSAGE_FIELDS = (
    "message",
    "Message",
    "Error",
    "error_description",
    "title",
    "detail",
)
SAFE_PROVIDER_ERROR_CODE_FIELDS = ("errorCode", "error_code", "code", "error")
SAFE_PROVIDER_ERROR_CODE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")
SENSITIVE_ERROR_TEXT_PATTERN = re.compile(
    r"\b(?:authorization|bearer|basic|access[_ -]?token|refresh[_ -]?token|"
    r"id[_ -]?token|client[_ -]?secret|password|cookie|api[_ -]?key)\b",
    flags=re.IGNORECASE,
)


def find_repo_root(start: Path) -> Path:
    """Find the FSCR checkout without assuming how the script was invoked."""

    for candidate in (start, *start.parents):
        if (candidate / "core" / "fusion-api" / "rest-api-client" / "scripts").is_dir():
            return candidate
    raise RuntimeError("Could not locate the FSCR repository root with the required layout.")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
REST_CLIENT_SCRIPTS = REPO_ROOT / "core" / "fusion-api" / "rest-api-client" / "scripts"
sys.path.insert(0, str(REST_CLIENT_SCRIPTS))

import rest_client_common  # noqa: E402


class FeatureStatesError(RuntimeError):
    """Raised when a feature-state lookup cannot return a safe, valid result."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        provider_message: str | None = None,
        provider_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.provider_message = provider_message
        self.provider_code = provider_code


@dataclass(frozen=True)
class OAuthOptions:
    """OAuth options consumed by the existing standard Fusion REST client."""

    redirect_url: str | None = None
    auth_code: str | None = None
    open_browser: bool = True
    callback_timeout: int = rest_client_common.DEFAULT_CALLBACK_TIMEOUT_SECONDS
    access_token: str | None = None
    force_login: bool = False


@dataclass(frozen=True)
class FeatureStatesResult:
    """A strict, sanitized result for one exact ``featureStates`` lookup."""

    feature_codes: tuple[str, ...]
    feature_mode: str
    items: tuple[dict[str, Any], ...]
    feature_states: dict[str, bool]
    audit_summary: dict[str, Any]

    def as_evidence(self) -> dict[str, Any]:
        """Return only the normalized records expected by dependent skills."""

        return {"items": [dict(item) for item in self.items]}

    def as_dict(self) -> dict[str, Any]:
        """Return a safe machine-readable summary without tokens or raw URLs."""

        return {
            "status": "verified",
            "feature_codes": list(self.feature_codes),
            "feature_mode": self.feature_mode,
            "feature_states": dict(self.feature_states),
            "evidence": self.as_evidence(),
            "audit_summary": dict(self.audit_summary),
        }


def _validate_feature_mode(feature_mode: str) -> str:
    if not isinstance(feature_mode, str) or not FEATURE_MODE_PATTERN.fullmatch(feature_mode):
        raise FeatureStatesError("feature_mode must be an uppercase Fusion feature mode code.")
    return feature_mode


def _validate_feature_codes(feature_codes: Sequence[str]) -> tuple[str, ...]:
    if not feature_codes:
        raise FeatureStatesError("At least one feature code is required.")
    normalized: list[str] = []
    for feature_code in feature_codes:
        if not isinstance(feature_code, str) or not FEATURE_CODE_PATTERN.fullmatch(feature_code):
            raise FeatureStatesError("Each feature code must be an uppercase Fusion feature code.")
        if feature_code in normalized:
            raise FeatureStatesError(f"Feature code {feature_code} was supplied more than once.")
        normalized.append(feature_code)
    return tuple(normalized)


def build_feature_states_query(feature_codes: Sequence[str], feature_mode: str) -> str:
    """Build the exact Fusion query while validating every supplied identifier."""

    codes = _validate_feature_codes(feature_codes)
    mode = _validate_feature_mode(feature_mode)
    quoted_codes = ",".join(f"'{code}'" for code in codes)
    return f"FeatureMode='{mode}' AND FeatureCode IN ({quoted_codes})"


def _decode_response(content: bytes) -> Mapping[str, Any]:
    if not isinstance(content, bytes):
        raise FeatureStatesError("Fusion featureStates returned an invalid response body.")
    if len(content) > MAX_FEATURE_STATES_RESPONSE_BYTES:
        raise FeatureStatesError(
            "Fusion featureStates response exceeded the safe response-size limit."
        )
    try:
        payload = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FeatureStatesError("Fusion featureStates returned malformed JSON.") from exc
    if not isinstance(payload, Mapping):
        raise FeatureStatesError("Fusion featureStates must return a JSON object.")
    return payload


def _safe_provider_error_text(value: Any) -> str | None:
    """Return a bounded plain-text provider message, or suppress it entirely."""

    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized or len(normalized) > MAX_PROVIDER_ERROR_MESSAGE_CHARS:
        return None
    if "<" in normalized or ">" in normalized:
        return None
    if SENSITIVE_ERROR_TEXT_PATTERN.search(normalized):
        return None
    return normalized


def _safe_provider_error_code(value: Any) -> str | None:
    """Return a short provider error code only when it is a plain identifier."""

    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized or len(normalized) > MAX_PROVIDER_ERROR_CODE_CHARS:
        return None
    if not SAFE_PROVIDER_ERROR_CODE_PATTERN.fullmatch(normalized):
        return None
    if SENSITIVE_ERROR_TEXT_PATTERN.search(normalized):
        return None
    return normalized


def _safe_fusion_business_error_details(body: Any) -> tuple[str | None, str | None]:
    """Extract only explicitly allowlisted, non-sensitive Fusion error details.

    The normal REST client preserves the raw error body in ``FusionHttpError``.
    That body can contain HTML, request echoes, or credential material, so this
    helper accepts only a small JSON object and only known message/code fields.
    """

    if not isinstance(body, str) or not body or len(body) > MAX_PROVIDER_ERROR_BODY_CHARS:
        return None, None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return None, None
    if not isinstance(payload, Mapping):
        return None, None

    candidates: list[Mapping[str, Any]] = [payload]
    nested_error = payload.get("error")
    if isinstance(nested_error, Mapping):
        candidates.append(nested_error)

    provider_message: str | None = None
    provider_code: str | None = None
    for candidate in candidates:
        if provider_message is None:
            for field in SAFE_PROVIDER_ERROR_MESSAGE_FIELDS:
                provider_message = _safe_provider_error_text(candidate.get(field))
                if provider_message is not None:
                    break
        if provider_code is None:
            for field in SAFE_PROVIDER_ERROR_CODE_FIELDS:
                provider_code = _safe_provider_error_code(candidate.get(field))
                if provider_code is not None:
                    break
        if provider_message is not None and provider_code is not None:
            break
    return provider_message, provider_code


def _feature_states_http_error(
    error: rest_client_common.FusionHttpError, *, after_token_refresh: bool = False
) -> FeatureStatesError:
    """Convert a transport error into a safe, actionable feature-state error."""

    provider_message, provider_code = _safe_fusion_business_error_details(
        getattr(error, "body", None)
    )
    message = f"Fusion featureStates returned HTTP {error.status_code}"
    if after_token_refresh:
        message += " after token refresh"
    if provider_message is not None:
        message += f": {provider_message}"
    if provider_code is not None and provider_code not in (provider_message or ""):
        message += f" [{provider_code}]"
    return FeatureStatesError(
        message + ".",
        http_status=error.status_code,
        provider_message=provider_message,
        provider_code=provider_code,
    )


def _normalize_items(
    payload: Mapping[str, Any], *, feature_codes: tuple[str, ...], feature_mode: str
) -> tuple[tuple[dict[str, Any], ...], dict[str, bool]]:
    has_more = payload.get("hasMore")
    if has_more is not None and type(has_more) is not bool:
        raise FeatureStatesError("Fusion featureStates hasMore must be a boolean.")
    if has_more is True:
        raise FeatureStatesError(
            "Fusion featureStates response is paginated and cannot prove the exact requested state set."
        )
    raw_items = payload.get("items")
    if not isinstance(raw_items, list):
        raise FeatureStatesError("Fusion featureStates response must contain an items array.")
    count = payload.get("count")
    if count is not None and (type(count) is not int or count != len(raw_items)):
        raise FeatureStatesError(
            "Fusion featureStates count must exactly match the returned items array."
        )

    expected = set(feature_codes)
    states: dict[str, bool] = {}
    normalized_by_code: dict[str, dict[str, Any]] = {}
    for raw_item in raw_items:
        if not isinstance(raw_item, Mapping):
            raise FeatureStatesError("Each Fusion featureStates item must be an object.")
        feature_code = raw_item.get("FeatureCode")
        returned_mode = raw_item.get("FeatureMode")
        status_flag = raw_item.get("StatusFlag")
        if feature_code not in expected:
            raise FeatureStatesError("Fusion featureStates returned an unexpected feature code.")
        if returned_mode != feature_mode:
            raise FeatureStatesError(
                f"Fusion feature {feature_code} must have FeatureMode {feature_mode}."
            )
        if type(status_flag) is not bool:
            raise FeatureStatesError(
                f"Fusion feature {feature_code} must have a boolean StatusFlag."
            )
        if feature_code in states:
            raise FeatureStatesError(
                f"Fusion featureStates returned duplicate feature code {feature_code}."
            )
        states[feature_code] = status_flag
        normalized_by_code[feature_code] = {
            "FeatureCode": feature_code,
            "FeatureMode": returned_mode,
            "StatusFlag": status_flag,
        }

    missing = [feature_code for feature_code in feature_codes if feature_code not in states]
    if missing:
        raise FeatureStatesError(
            "Fusion featureStates response is missing requested feature code(s): "
            + ", ".join(missing)
            + "."
        )
    if len(raw_items) != len(feature_codes):
        raise FeatureStatesError(
            "Fusion featureStates response must contain exactly the requested feature records."
        )
    return tuple(normalized_by_code[code] for code in feature_codes), states


class FeatureStatesReader:
    """Reusable read-only adapter over the existing standard Fusion REST client."""

    def __init__(
        self,
        properties: Mapping[str, str],
        *,
        token_cache: str | None = DEFAULT_TOKEN_CACHE,
        timeout: int = 60,
        oauth_options: OAuthOptions | None = None,
        token_provider: Callable[..., str] = rest_client_common.get_token,
        requester: Callable[..., tuple[bytes, dict[str, str], int]] = rest_client_common.request_bytes,
    ) -> None:
        if not isinstance(timeout, int) or not 1 <= timeout <= 300:
            raise FeatureStatesError("timeout must be an integer between 1 and 300 seconds.")
        try:
            base_properties = dict(properties)
            rest_client_common.require_props(base_properties, ["environment", "restBaseUrl"])
            oauth_properties = rest_client_common.props_with_scope_property(
                base_properties, "scope"
            )
        except ValueError as exc:
            raise FeatureStatesError(str(exc)) from exc

        self._properties = base_properties
        self._oauth_properties = oauth_properties
        self._token_cache = token_cache
        self._timeout = timeout
        self._oauth_options = oauth_options or OAuthOptions()
        self._token_provider = token_provider
        self._requester = requester

    @classmethod
    def from_properties_file(
        cls,
        properties_path: Path,
        *,
        token_cache: str | None = DEFAULT_TOKEN_CACHE,
        timeout: int = 60,
        oauth_options: OAuthOptions | None = None,
    ) -> "FeatureStatesReader":
        try:
            properties = rest_client_common.read_properties(properties_path)
        except (OSError, ValueError) as exc:
            raise FeatureStatesError("Unable to read the Fusion OAuth properties file.") from exc
        return cls(
            properties,
            token_cache=token_cache,
            timeout=timeout,
            oauth_options=oauth_options,
        )

    def _token_args(self) -> argparse.Namespace:
        options = self._oauth_options
        return argparse.Namespace(
            access_token=options.access_token,
            redirect_url=options.redirect_url,
            auth_code=options.auth_code,
            open_browser=options.open_browser,
            callback_timeout=options.callback_timeout,
            token_cache=self._token_cache,
            force_login=options.force_login,
        )

    def _access_token(self, *, force_login: bool = False) -> str:
        return self._token_provider(
            self._oauth_properties,
            self._token_args(),
            force_login=force_login,
        )

    def _oauth_request(
        self, *, url: str, access_token: str
    ) -> tuple[bytes, dict[str, str], int]:
        return self._requester(
            self._properties,
            url,
            method="GET",
            access_token=access_token,
            headers={"REST-Framework-Version": FEATURE_STATES_REST_FRAMEWORK_VERSION},
            json_body=None,
            timeout=self._timeout,
        )

    def read(
        self, feature_codes: Sequence[str], *, feature_mode: str = "COMBO"
    ) -> FeatureStatesResult:
        """Read exactly the requested current feature states through one GET request."""

        codes = _validate_feature_codes(feature_codes)
        mode = _validate_feature_mode(feature_mode)
        query = build_feature_states_query(codes, mode)
        url = rest_client_common.build_url(
            self._properties,
            FEATURE_STATES_PATH,
            {"onlyData": "true", "q": query},
        )

        retry_count = 0
        try:
            content, headers, status = self._oauth_request(
                url=url, access_token=self._access_token()
            )
        except rest_client_common.FusionHttpError as exc:
            if (
                exc.status_code not in {401, 403}
                or self._oauth_options.access_token
                or self._oauth_options.auth_code
            ):
                raise _feature_states_http_error(exc) from exc
            retry_count = 1
            try:
                content, headers, status = self._oauth_request(
                    url=url,
                    access_token=self._access_token(force_login=True),
                )
            except rest_client_common.FusionHttpError as retry_exc:
                raise _feature_states_http_error(retry_exc, after_token_refresh=True) from retry_exc
            except (OSError, TimeoutError, RuntimeError, ValueError) as retry_exc:
                raise FeatureStatesError(
                    "Unable to call Fusion featureStates after token refresh."
                ) from retry_exc
        except (OSError, TimeoutError, RuntimeError, ValueError) as exc:
            raise FeatureStatesError("Unable to call Fusion featureStates.") from exc

        if not 200 <= status < 300:
            raise FeatureStatesError(
                f"Fusion featureStates returned unexpected HTTP {status}.", http_status=status
            )
        items, states = _normalize_items(
            _decode_response(content), feature_codes=codes, feature_mode=mode
        )
        return FeatureStatesResult(
            feature_codes=codes,
            feature_mode=mode,
            items=items,
            feature_states=states,
            audit_summary={
                "method": "GET",
                "endpoint_path": FEATURE_STATES_PATH,
                "auth_mode": "oauth",
                "rest_framework_version": FEATURE_STATES_REST_FRAMEWORK_VERSION,
                "http_status": status,
                "retry_count": retry_count,
                "response_record_count": len(items),
            },
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read exact current Fusion featureStates records. This command is read-only."
    )
    parser.add_argument("--feature-code", action="append", required=True)
    parser.add_argument("--feature-mode", default="COMBO")
    parser.add_argument("--properties", default=str(REPO_ROOT / "core" / "auth" / "fusionEnv.properties"))
    parser.add_argument("--token-cache", default=DEFAULT_TOKEN_CACHE)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--auth-code")
    parser.add_argument("--redirect-url")
    parser.add_argument(
        "--callback-timeout",
        type=int,
        default=rest_client_common.DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    )
    parser.add_argument("--force-login", action="store_true")
    parser.add_argument("--access-token", help="Existing bearer token; never persist it in output.")
    parser.add_argument("--no-open-browser", action="store_true")
    parser.add_argument("--output", help="Optional path for the sanitized result JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    oauth_options = OAuthOptions(
        redirect_url=args.redirect_url,
        auth_code=args.auth_code,
        open_browser=not args.no_open_browser,
        callback_timeout=args.callback_timeout,
        access_token=args.access_token,
        force_login=args.force_login,
    )
    result = FeatureStatesReader.from_properties_file(
        Path(args.properties),
        token_cache=args.token_cache,
        timeout=args.timeout,
        oauth_options=oauth_options,
    ).read(args.feature_code, feature_mode=args.feature_mode)
    rendered = json.dumps(result.as_dict(), indent=2, sort_keys=True)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FeatureStatesError as exc:
        print(json.dumps({"status": "failed", "message": str(exc)}), file=sys.stderr)
        raise SystemExit(1)
