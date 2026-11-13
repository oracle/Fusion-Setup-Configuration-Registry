#!/usr/bin/env python3
"""Search published content for one Sales Play using managed OAuth."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
CORE_REST_SCRIPTS = REPOSITORY_ROOT / "core" / "fusion-api" / "rest-api-client" / "scripts"
sys.path.insert(0, str(CORE_REST_SCRIPTS))

from rest_client_common import (  # noqa: E402
    FusionHttpError,
    build_parser,
    build_url,
    get_token,
    load_json_body,
    parse_repeated_key_values,
    read_properties,
    request_bytes,
    require_props,
    write_or_print,
)


DEFAULT_TOKEN_CACHE = "auto"
CONTENT_SEARCH_PATH = "/api/knowledge-management/v2/contentIntelligence"
SALES_PLAY_FILTER = "contentTypeAttributes.ORA_CX_SALES_PLAY.SALES_PLAY"


class ContentSearchValidationError(ValueError):
    """A safe, fixed validation message that may be shown by the CLI."""


def validate_content_search(args) -> tuple[dict, dict[str, str]]:
    """Enforce the semantic-read contract before authentication or transport."""
    if args.method != "POST" or args.endpoint != CONTENT_SEARCH_PATH:
        raise ContentSearchValidationError(
            "Only POST to the exact relative Content Intelligence path is supported"
        )
    if args.query or args.service != "standard" or args.scim_only:
        raise ContentSearchValidationError("Query and service overrides are not supported")
    if args.access_token or args.token_cache != "auto":
        raise ContentSearchValidationError("Use the managed OAuth cache with --token-cache auto")
    try:
        headers = parse_repeated_key_values(
            args.header, separator_hint="header Name=value or Name: value"
        )
    except ValueError:
        raise ContentSearchValidationError("Malformed Content Intelligence header") from None
    if any(name.lower() not in {"accept", "content-type"}
           or value.lower() != "application/json" for name, value in headers.items()):
        raise ContentSearchValidationError(
            "Only application/json Accept and Content-Type headers are supported"
        )

    body = load_json_body(args)
    if not isinstance(body, dict) or set(body) != {"userInput", "connectorDetails", "filters"}:
        raise ContentSearchValidationError("Use the documented Content Intelligence request body")
    if body["connectorDetails"] != {"connectorId": "ORA_CX_SALES_PLAY"}:
        raise ContentSearchValidationError("Use the fixed Sales Play connector")
    try:
        user_input = json.loads(body["userInput"])
    except (ValueError, TypeError):
        raise ContentSearchValidationError("userInput must contain a serialized JSON object") from None
    if (not isinstance(user_input, dict)
            or set(user_input) != {"additionalFilters", "question", "extractFiltersFromQuestion"}
            or user_input["additionalFilters"] != []
            or user_input["extractFiltersFromQuestion"] is not False
            or not isinstance(user_input["question"], str)
            or not user_input["question"].strip()):
        raise ContentSearchValidationError(
            "Require a question, empty additionalFilters and disabled filter extraction"
        )
    filters = body["filters"]
    if not isinstance(filters, list) or len(filters) != 2:
        raise ContentSearchValidationError("Require the two fixed published Sales Play filters")
    values = {}
    for item in filters:
        if (not isinstance(item, dict) or set(item) != {"fieldName", "value", "operator"}
                or not isinstance(item["fieldName"], str)
                or item["fieldName"] not in {"contentState", SALES_PLAY_FILTER}
                or item["fieldName"] in values or item["operator"] != "eq"
                or not isinstance(item["value"], str) or not item["value"].strip()):
            raise ContentSearchValidationError("Require the fixed equality filters and one Sales Play ID")
        values[item["fieldName"]] = item["value"]
    if values.get("contentState") != "PUBLISHED" or SALES_PLAY_FILTER not in values:
        raise ContentSearchValidationError("Require published content for one exact Sales Play ID")
    return body, headers


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
            "Search published Sales Play content. Only POST to the exact relative "
            "Content Intelligence path with its fixed request contract is supported."
        ),
        default_token_cache=DEFAULT_TOKEN_CACHE,
    )
    args = parser.parse_args()
    json_body, headers = validate_content_search(args)

    props = read_properties(Path(args.properties))
    require_props(props, ["environment", "restBaseUrl"])
    auth_props = select_knowledge_management_scope(props)

    url = build_url(auth_props, CONTENT_SEARCH_PATH, {})
    access_token = get_token(auth_props, args)

    try:
        content, response_headers, status = request_bytes(
            auth_props,
            url,
            method="POST",
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
            method="POST",
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
    try:
        return run_knowledge_client()
    except ContentSearchValidationError as exc:
        print(f"Invalid Content Intelligence request: {exc}", file=sys.stderr)
    except FusionHttpError as exc:
        print(
            f"Content Intelligence failed (HTTP {exc.status_code}) at {CONTENT_SEARCH_PATH}; "
            "response details suppressed",
            file=sys.stderr,
        )
    except Exception as exc:
        print(
            f"Content Intelligence failed ({type(exc).__name__}); details suppressed",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
