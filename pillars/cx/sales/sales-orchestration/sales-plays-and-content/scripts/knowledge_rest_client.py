#!/usr/bin/env python3
"""Invoke Oracle Fusion Knowledge Management REST APIs with selected OAuth scope."""

from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
CORE_REST_SCRIPTS = REPOSITORY_ROOT / "core" / "fusion-api" / "rest-api-client" / "scripts"
sys.path.insert(0, str(CORE_REST_SCRIPTS))

from rest_client_common import (  # noqa: E402
    FusionHttpError,
    build_parser,
    build_url,
    endpoint_path,
    get_token,
    load_json_body,
    parse_repeated_key_values,
    read_properties,
    request_bytes,
    require_props,
    write_or_print,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOKEN_CACHE = "auto"


def select_knowledge_management_scope(props: dict[str, str]) -> dict[str, str]:
    """Return OAuth properties narrowed to the one Knowledge Management scope."""
    regular_scope = props.get("scope", "")
    if not regular_scope:
        raise ValueError("Missing required OAuth scope property: scope")

    matches = [value for value in regular_scope.split() if "knowledge-management" in value]
    if len(matches) != 1:
        raise ValueError(
            "Regular OAuth scope must include exactly one knowledge-management scope token"
        )

    scoped_props = dict(props)
    scoped_props["scope"] = matches[0]
    return scoped_props


def run_knowledge_client() -> int:
    parser = build_parser(
        description=(
            "Invoke Oracle Fusion Knowledge Management REST APIs with the "
            "knowledge-management scope selected from the regular scope property."
        ),
        default_token_cache=DEFAULT_TOKEN_CACHE,
    )
    args = parser.parse_args()
    if args.access_token:
        raise ValueError("Explicit access tokens are not supported; use the managed OAuth cache")

    props = read_properties(Path(args.properties))
    require_props(props, ["environment", "restBaseUrl"])
    auth_props = select_knowledge_management_scope(props)

    path = endpoint_path(args.endpoint)
    if not path.startswith("/api/knowledge-management"):
        raise ValueError("This client only supports endpoints under /api/knowledge-management")

    query_params = parse_repeated_key_values(args.query, separator_hint="query key=value")
    headers = parse_repeated_key_values(
        args.header, separator_hint="header Name=value or Name: value"
    )
    json_body = load_json_body(args)
    url = build_url(auth_props, args.endpoint, query_params)
    access_token = get_token(auth_props, args)

    try:
        content, response_headers, status = request_bytes(
            auth_props,
            url,
            method=args.method,
            access_token=access_token,
            headers=headers,
            json_body=json_body,
            timeout=args.timeout,
        )
    except FusionHttpError as exc:
        if exc.status_code not in {401, 403}:
            raise
        print("Cached access token was rejected by Fusion. Running login flow again.", file=sys.stderr)
        access_token = get_token(auth_props, args, force_login=True)
        content, response_headers, status = request_bytes(
            auth_props,
            url,
            method=args.method,
            access_token=access_token,
            headers=headers,
            json_body=json_body,
            timeout=args.timeout,
        )

    if args.output:
        print(f"HTTP {status}")
    write_or_print(content, response_headers, args)
    return 0


def main() -> int:
    return run_knowledge_client()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
