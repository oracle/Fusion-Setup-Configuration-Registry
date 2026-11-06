#!/usr/bin/env python3
"""Validate retained BU lookup pages offline; never sends a REST request."""
import argparse
import json
from pathlib import Path
import re


def resolve_business_unit(evidence):
    if not isinstance(evidence, dict) or not isinstance(evidence.get('requestContext'), dict):
        raise ValueError('REFERENCE_CONTEXT: Expected scoped lookup evidence.')
    context = evidence.get('requestContext', {})
    for field in ('targetOrigin', 'identity', 'language', 'runId', 'acquiredAt'):
        if not isinstance(context.get(field), str) or not context[field].strip():
            raise ValueError('REFERENCE_CONTEXT: Missing lookup scope: '+field)
    if not isinstance(context.get('headers', {}), dict):
        raise ValueError('REFERENCE_CONTEXT: Expected non-secret request headers.')
    headers = {str(k).lower(): str(v) for k, v in context.get('headers', {}).items()}
    version = headers.get('rest-framework-version')
    if version is None:
        version = context.get('defaultFrameworkVersion')
        if version is None or not context.get('defaultVersionEvidence'):
            raise ValueError('REFERENCE_CONTEXT: Resolve framework version/header policy before lookup.')
    if not re.fullmatch(r'[1-9][0-9]*', str(version)):
        raise ValueError('REFERENCE_CONTEXT: Invalid framework version.')
    query = context.get('q', '')
    if not isinstance(query, str):
        raise ValueError('REFERENCE_CONTEXT: Missing query form.')
    if int(version) == 1 and re.search(r'\band\s+[A-Za-z_][A-Za-z0-9_]*\s*=', query, re.I):
        raise ValueError('REFERENCE_CONTEXT: Expanded compound q requires a compatible framework version.')
    pages = evidence.get('pages')
    if not isinstance(pages, list) or not pages:
        raise ValueError('REFERENCE_INCOMPLETE: Retain all lookup pages.')
    offset, rows, identities = 0, [], set()
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError('REFERENCE_INCOMPLETE: Expected a collection page.')
        items = page.get('items')
        count, more = page.get('count'), page.get('hasMore')
        if (not isinstance(items, list) or type(count) is not int or count != len(items)
                or page.get('offset') != offset or type(more) is not bool):
            raise ValueError('REFERENCE_INCOMPLETE: Malformed page count, offset or hasMore.')
        if more and (not items or index == len(pages)-1):
            raise ValueError('REFERENCE_INCOMPLETE: More BU pages remain; advance offset by returned count.')
        if not more and index != len(pages)-1:
            raise ValueError('REFERENCE_INCOMPLETE: Unexpected pages after terminal page.')
        for row in items:
            if not isinstance(row, dict):
                raise ValueError('REFERENCE_INCOMPLETE: Expected a BU row.')
            identity = row.get('BusinessUnitId')
            if (isinstance(identity, bool) or not isinstance(identity, (str, int))
                    or not str(identity).strip() or not isinstance(row.get('BusinessUnitName'), str)
                    or not row['BusinessUnitName'].strip() or type(row.get('ActiveFlag')) is not bool):
                raise ValueError('REFERENCE_INCOMPLETE: Missing BU identity, name or active state.')
            identity = str(identity)
            if identity in identities:
                raise ValueError('REFERENCE_INCOMPLETE: Repeated BU identity across pages.')
            identities.add(identity)
            rows.append(row)
        offset += count
    intent = evidence.get('intent')
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError('REFERENCE_CONTEXT: Supply the intended business unit name.')
    normalize = lambda s: ' '.join(s.split()).casefold()
    matches = [r for r in rows if r['ActiveFlag'] and normalize(r['BusinessUnitName']) == normalize(intent)]
    if not matches:
        raise ValueError('REFERENCE_MISSING: No active match in this completed visible query scope; this does not prove global absence. Reconcile existing export references and lookup visibility before proposing a replacement.')
    if len(matches) != 1:
        raise ValueError('REFERENCE_AMBIGUOUS: Multiple active business units match.')
    return {'status': 'identity_only', 'BusinessUnitId': matches[0]['BusinessUnitId'],
            'BusinessUnitName': matches[0]['BusinessUnitName'], 'pageCount': len(pages),
            'rowCount': len(rows), 'frameworkVersion': str(version),
            'scope': {k: context[k] for k in ('targetOrigin', 'identity', 'language', 'runId', 'acquiredAt')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = resolve_business_unit(json.loads(args.input.read_text()))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError) as error:
        print(str(error))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
