#!/usr/bin/env python3
"""Inventory source XML paths and target tags used by Oracle Payments XSL templates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


XSL_NS = "http://www.w3.org/1999/XSL/Transform"
PATH_RE = re.compile(
    r"(?<![\w:-])(/?[A-Za-z_][\w.-]*(?:\[[^\]]+\])?(?:/[A-Za-z_][\w.-]*(?:\[[^\]]+\])?)+)"
)
ACCOUNT_SETTING_RE = re.compile(
    r"(?:contains\s*\(\s*Name\s*,\s*['\"]([^'\"]+)['\"]\)|"
    r"AccountSettings\s*\[\s*Name\s*=\s*['\"]([^'\"]+)['\"]\])"
)


def split_tag(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        namespace, local = tag[1:].split("}", 1)
        return namespace, local
    return "", tag


def clean_path(path: str) -> str | None:
    path = path.strip().lstrip("/")
    if not path:
        return None
    first = path.split("/", 1)[0]
    if first in {"xsl", "xml", "xmlns"}:
        return None
    if first.startswith("$"):
        return None
    if "(" in first:
        return None
    return path


def extract_paths(expression: str) -> set[str]:
    paths: set[str] = set()
    for match in PATH_RE.finditer(expression):
        cleaned = clean_path(match.group(1))
        if cleaned:
            paths.add(cleaned)
    return paths


def element_text(element: ET.Element) -> str:
    parts = [text.strip() for text in element.itertext() if text and text.strip()]
    return " ".join(parts)


def analyze_file(path: Path) -> dict:
    parser = ET.XMLParser()
    root = ET.parse(path, parser=parser).getroot()

    target_elements: Counter[str] = Counter()
    output_namespaces: Counter[str] = Counter()
    source_paths: Counter[str] = Counter()
    account_settings: Counter[str] = Counter()
    variables: dict[str, str] = {}
    conditions: list[str] = []
    attribute_expressions: dict[str, list[str]] = defaultdict(list)

    for elem in root.iter():
        namespace, local = split_tag(elem.tag)
        if namespace != XSL_NS:
            target_elements[local] += 1
            if namespace:
                output_namespaces[namespace] += 1

        if namespace == XSL_NS and local == "variable":
            name = elem.attrib.get("name")
            if name:
                variables[name] = elem.attrib.get("select") or element_text(elem)

        for attr_name, attr_value in elem.attrib.items():
            if attr_name in {"select", "test", "match", "use"}:
                attribute_expressions[attr_name].append(attr_value)
                for source_path in extract_paths(attr_value):
                    source_paths[source_path] += 1
                for setting_match in ACCOUNT_SETTING_RE.finditer(attr_value):
                    setting = setting_match.group(1) or setting_match.group(2)
                    if setting:
                        account_settings[setting] += 1
                if attr_name == "test":
                    conditions.append(attr_value)

    return {
        "file": str(path),
        "output_namespaces": dict(output_namespaces.most_common()),
        "target_elements": dict(target_elements.most_common()),
        "source_paths": dict(source_paths.most_common()),
        "account_settings": dict(account_settings.most_common()),
        "variables": variables,
        "conditions": conditions,
        "attribute_expression_counts": {
            name: len(values) for name, values in sorted(attribute_expressions.items())
        },
    }


def to_markdown(results: list[dict]) -> str:
    lines: list[str] = ["# XSLT Usage Inventory", ""]
    for result in results:
        lines.extend([f"## {result['file']}", ""])

        namespaces = result["output_namespaces"]
        if namespaces:
            lines.append("### Output Namespaces")
            for namespace, count in namespaces.items():
                lines.append(f"- `{namespace}` ({count})")
            lines.append("")

        lines.append("### Account Settings")
        if result["account_settings"]:
            for name, count in result["account_settings"].items():
                lines.append(f"- `{name}` ({count})")
        else:
            lines.append("- None detected")
        lines.append("")

        lines.append("### Source Paths")
        if result["source_paths"]:
            for source_path, count in result["source_paths"].items():
                lines.append(f"- `{source_path}` ({count})")
        else:
            lines.append("- None detected")
        lines.append("")

        lines.append("### Target Elements")
        for tag, count in list(result["target_elements"].items())[:200]:
            lines.append(f"- `{tag}` ({count})")
        if len(result["target_elements"]) > 200:
            lines.append(f"- ... {len(result['target_elements']) - 200} more")
        lines.append("")

        lines.append("### Variables")
        if result["variables"]:
            for name, value in list(result["variables"].items())[:100]:
                compact = " ".join(str(value).split())
                if len(compact) > 180:
                    compact = compact[:177] + "..."
                lines.append(f"- `${name}` = `{compact}`")
        else:
            lines.append("- None detected")
        lines.append("")

        lines.append("### Condition Count")
        lines.append(f"- `{len(result['conditions'])}` `test` expressions")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="XSL files to inspect")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--output", help="Optional output file")
    args = parser.parse_args(argv)

    results = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(path)
        results.append(analyze_file(path))

    if args.format == "json":
        rendered = json.dumps(results, indent=2, sort_keys=True)
    else:
        rendered = to_markdown(results)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
