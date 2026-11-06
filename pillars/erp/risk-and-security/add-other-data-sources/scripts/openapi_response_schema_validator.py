#!/usr/bin/env python3
"""Validate that documented successful JSON responses are usable for extraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


HTTP_METHODS = frozenset({"get", "put", "post", "delete", "patch", "head", "options", "trace"})


def _json_pointer(document: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise ValueError(f"Only local OpenAPI references are supported: {reference}")
    current: Any = document
    for token in reference[2:].split("/"):
        if not isinstance(current, dict):
            raise ValueError(f"OpenAPI reference does not resolve: {reference}")
        current = current.get(token.replace("~1", "/").replace("~0", "~"))
    if current is None:
        raise ValueError(f"OpenAPI reference does not resolve: {reference}")
    return current


def _resolve_schema(document: dict[str, Any], schema: Any, references: tuple[str, ...] = ()) -> dict[str, Any]:
    if not isinstance(schema, dict):
        raise ValueError("Response schema must be an object.")
    reference = schema.get("$ref")
    if not isinstance(reference, str):
        return schema
    if reference in references:
        raise ValueError(f"Cyclic OpenAPI response schema reference: {reference}")
    resolved = _resolve_schema(document, _json_pointer(document, reference), (*references, reference))
    return {**resolved, **{key: value for key, value in schema.items() if key != "$ref"}}


def _leaf_count(document: dict[str, Any], schema: Any, path: str, references: tuple[str, ...] = ()) -> int:
    resolved = _resolve_schema(document, schema, references)
    for composition in ("oneOf", "anyOf", "not"):
        if composition in resolved:
            raise ValueError(f"{path} uses unsupported {composition}; extraction attributes would be ambiguous.")
    if "allOf" in resolved:
        branches = resolved["allOf"]
        if not isinstance(branches, list) or not branches:
            raise ValueError(f"{path} has an invalid allOf response schema.")
        own = {key: value for key, value in resolved.items() if key != "allOf"}
        own_leaf_count = (
            _leaf_count(document, own, path, references)
            if any(key in own for key in ("$ref", "type", "properties", "items"))
            else 0
        )
        return own_leaf_count + sum(
            _leaf_count(document, branch, path, references) for branch in branches
        )

    schema_type = resolved.get("type")
    properties = resolved.get("properties")
    if schema_type == "object" or isinstance(properties, dict):
        if not isinstance(properties, dict) or not properties:
            raise ValueError(f"{path} is an object response schema without documented properties.")
        return sum(
            _leaf_count(document, child, f"{path}.{name}", references)
            for name, child in properties.items()
        )
    if schema_type == "array":
        if "items" not in resolved:
            raise ValueError(f"{path} is an array response schema without an items schema.")
        return _leaf_count(document, resolved["items"], f"{path}[]", references)
    if isinstance(schema_type, str) and schema_type:
        return 1
    raise ValueError(f"{path} has no derivable type, properties, or array items.")


def _is_success(status: Any) -> bool:
    return isinstance(status, str) and len(status) == 3 and status.isdigit() and status.startswith("2")


def _is_json_media_type(value: Any) -> bool:
    return isinstance(value, str) and (value == "application/json" or value.endswith("+json"))


def validate_openapi_response_schemas(document: Any) -> int:
    """Return validated extraction leaf count or raise ValueError before approval creation."""

    if not isinstance(document, dict) or not isinstance(document.get("paths"), dict):
        raise ValueError("OpenAPI document must be an object with paths.")
    openapi_v3 = isinstance(document.get("openapi"), str)
    swagger_v2 = document.get("swagger") == "2.0"
    if not (openapi_v3 or swagger_v2):
        raise ValueError("Document must declare an OpenAPI 3 or Swagger 2.0 version.")

    leaf_count = 0
    for path, path_item in document["paths"].items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            responses = operation.get("responses")
            if not isinstance(responses, dict):
                raise ValueError(f"{method.upper()} {path} has no response definitions.")
            for status, response in responses.items():
                if not _is_success(status) or not isinstance(response, dict):
                    continue
                if openapi_v3:
                    content = response.get("content")
                    if content is None:
                        continue
                    if not isinstance(content, dict):
                        raise ValueError(f"{method.upper()} {path} {status} has invalid response content.")
                    for media_type, media in content.items():
                        if not _is_json_media_type(media_type):
                            continue
                        if not isinstance(media, dict) or "schema" not in media:
                            raise ValueError(f"{method.upper()} {path} {status} JSON response has no schema.")
                        leaf_count += _leaf_count(document, media["schema"], f"{method.upper()} {path} {status}")
                else:
                    produces = operation.get("produces", document.get("produces", []))
                    json_response = any(_is_json_media_type(media_type) for media_type in produces) if isinstance(produces, list) else True
                    if not json_response:
                        continue
                    if "schema" not in response:
                        raise ValueError(f"{method.upper()} {path} {status} JSON response has no schema.")
                    leaf_count += _leaf_count(document, response["schema"], f"{method.upper()} {path} {status}")
    if leaf_count == 0:
        raise ValueError("Specification has no eligible successful JSON extraction response with derivable leaves.")
    return leaf_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openapi-spec", type=Path, required=True)
    args = parser.parse_args()
    try:
        document = json.loads(args.openapi_spec.read_text(encoding="utf-8"))
        print(json.dumps({"status": "valid", "extraction_leaf_count": validate_openapi_response_schemas(document)}))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "invalid", "failure_class": "input_validation", "message": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
