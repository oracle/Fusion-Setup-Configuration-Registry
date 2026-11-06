#!/usr/bin/env python3
"""Programmatic read adapter for Oracle CPQ v19 operations.

This module belongs to the Fusion ABO pillar skill. It exposes a
relative-path-only GET surface; task capabilities
remain responsible for endpoint allowlists and response validation. Mutations
are deliberately absent from this public adapter.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "core" / "auth" / "fusion-oauth-authentication" / "scripts").is_dir():
            return candidate
    raise RuntimeError("Could not locate the FSCR repository root.")


CORE_ROOT = _find_repo_root(Path(__file__).resolve())
DEFAULT_PROPERTIES_PATH = CORE_ROOT / "core" / "auth" / "fusionEnv.properties"
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIRECTORY))

from cpq_rest_transport import (  # noqa: E402
    CpqClientError,
    CpqConfigurationError,
    CpqHttpError,
    CpqOAuthTransport,
    CpqResponse,
    CpqResponseError,
    CpqTransportError,
    OAuthOptions,
    build_cpq_oauth_properties,
    get_access_token,
    validate_cpq_base_url,
)
from fusion_auth import DEFAULT_CALLBACK_TIMEOUT_SECONDS, read_properties  # noqa: E402


class CpqRestClient:
    """Run caller-governed, read-only CPQ v19 REST operations."""

    def __init__(
        self,
        oauth_properties: Mapping[str, str],
        *,
        token_cache: str | None = None,
        timeout: int = 60,
        oauth_options: OAuthOptions | None = None,
        token_provider: Callable[..., str] = get_access_token,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        transport_options: dict[str, Any] = {
            "token_cache": token_cache,
            "timeout": timeout,
            "oauth_options": oauth_options,
            "token_provider": token_provider,
        }
        if opener is not None:
            transport_options["opener"] = opener
        self._transport = CpqOAuthTransport(oauth_properties, **transport_options)
        self._base_url = self._transport.base_url

    @classmethod
    def from_properties_file(
        cls,
        properties_path: Path,
        *,
        token_cache: str | None = None,
        timeout: int = 60,
        oauth_options: OAuthOptions | None = None,
    ) -> "CpqRestClient":
        try:
            properties = read_properties(properties_path)
        except (OSError, ValueError) as exc:
            # The shared parser can include the bad source line in its error;
            # keep potential local profile secrets out of CLI diagnostics.
            raise CpqConfigurationError("Unable to read the local CPQ OAuth properties file.") from exc
        return cls(
            properties,
            token_cache=token_cache,
            timeout=timeout,
            oauth_options=oauth_options,
        )

    def _access_token(self, *, force_login: bool = False) -> str:
        self._transport.ensure_authenticated(force_login=force_login)
        # Preserve the existing private compatibility hook without returning
        # the token itself to a caller.
        return "authenticated"

    def get_json(self, path: str) -> CpqResponse:
        """GET one relative CPQ v19 path selected by a governing caller."""

        return self._transport.get_json(path)

def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    """Add safe OAuth/connection arguments shared by CPQ client commands."""

    parser.add_argument("--properties", default=str(DEFAULT_PROPERTIES_PATH), help="Secure CPQ OAuth properties file.")
    parser.add_argument("--token-cache", help="Optional local OAuth token-cache path; keep it gitignored.")
    parser.add_argument("--timeout", type=int, default=60, help="HTTPS timeout in seconds (1-300).")
    parser.add_argument("--auth-code", help="OAuth authorization code, used only when OAuth login is required.")
    parser.add_argument("--code-verifier", help="PKCE verifier for --auth-code when PKCE is enabled.")
    parser.add_argument("--redirect-url", help="OAuth redirect URI override.")
    parser.add_argument("--callback-timeout", type=int, default=DEFAULT_CALLBACK_TIMEOUT_SECONDS)
    parser.add_argument("--no-open-browser", action="store_true", help="Do not open the OAuth browser automatically.")
    parser.add_argument("--force-login", action="store_true", help="Ignore a cached OAuth token for this read command.")


def client_from_args(args: argparse.Namespace) -> CpqRestClient:
    """Create the CPQ client without supporting raw tokens or basic credentials."""

    options = OAuthOptions(
        redirect_url=args.redirect_url,
        auth_code=args.auth_code,
        code_verifier=args.code_verifier,
        open_browser=not args.no_open_browser,
        callback_timeout=args.callback_timeout,
    )
    client = CpqRestClient.from_properties_file(
        Path(args.properties),
        token_cache=args.token_cache,
        timeout=args.timeout,
        oauth_options=options,
    )
    if args.force_login:
        client._access_token(force_login=True)  # noqa: SLF001 - explicit CLI login request
    return client
