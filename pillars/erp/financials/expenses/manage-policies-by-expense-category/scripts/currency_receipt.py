"""Verify host-recorded currency evidence for one immutable preparation operation.

Receipts are local audit evidence, not signatures, import approval or proof of
CSV acceptance. Captured eligibility is always recomputed from complete pages.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from currency_reference import classify, iso_day, request_plan

ROUTE = 'policy-currency-core-client-v1'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def origin(value):
    if not isinstance(value, str):
        raise ValueError('Explicit target HTTPS origin required')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.path not in {'', '/'} or parsed.query or parsed.fragment):
        raise ValueError('Explicit target HTTPS origin required')
    return 'https://' + parsed.netloc.lower()


def binding(workbook, baseline, runtime_contract, environment, target_origin, as_of):
    iso_day(as_of)
    if not isinstance(environment, str) or not environment or environment.strip() != environment:
        raise ValueError('Explicit target environment required')
    return {
        'workbook_sha256': digest(workbook), 'baseline_sha256': digest(baseline),
        'runtime_contract_sha256': digest(runtime_contract), 'environment': environment,
        'origin': origin(target_origin), 'as_of': as_of,
    }


def verify(receipt_path, expected_binding, entity, policy_name, operation, code):
    """Admit only the exact CurrencyCode covered by verified operation evidence."""
    path = Path(receipt_path)
    receipt = json.loads(path.read_text())
    if (receipt.get('schema_version') != '1.0' or receipt.get('route') != ROUTE
            or receipt.get('status') != 'captured' or receipt.get('binding') != expected_binding):
        raise ValueError('Currency receipt identity/binding mismatch')
    if receipt.get('adapter_sha256') != digest(__file__):
        raise ValueError('Currency receipt adapter changed; recapture required')
    wanted = {'entity': entity, 'policy_name': policy_name, 'operation': operation, 'currency_code': code}
    operations = receipt.get('operations')
    if (not isinstance(operations, list) or operations.count(wanted) != 1
            or operation not in {'create', 'update'} or not policy_name):
        raise ValueError('Currency receipt does not bind this exact operation')
    captures = receipt.get('currencies')
    if not isinstance(captures, dict) or code not in captures:
        raise ValueError('Currency receipt is missing the exact code')
    captures = captures[code]
    if not isinstance(captures, list) or not captures:
        raise ValueError('Currency receipt needs complete captured pages')
    pages, offset = [], 0
    for capture in captures:
        if not isinstance(capture, dict) or capture.get('request') != request_plan(code, expected_binding['as_of'], offset):
            raise ValueError('Currency receipt request differs from the declared GET')
        member = capture.get('response_file')
        # Evidence files must be immediate, nonsymlinked members beside the receipt.
        if (not isinstance(member, str) or member in {'', '.', '..'}
                or Path(member).name != member or '\\' in member):
            raise ValueError('Unsafe currency response evidence path')
        response = path.parent / member
        if response.is_symlink() or digest(response) != capture.get('response_sha256'):
            raise ValueError('Currency response evidence changed')
        if capture.get('http_status') != 200:
            raise ValueError('Currency request did not return HTTP 200')
        page = json.loads(response.read_text())
        pages.append(page)
        if not isinstance(page, dict) or not isinstance(page.get('items'), list):
            raise ValueError('Malformed currency response page')
        offset += len(page['items'])
    result = classify(pages, code, expected_binding['as_of'])
    if result.get('reference_resolved') is not True:
        raise ValueError('Currency is unresolved: ' + result['status'])
    return {'field': 'CurrencyCode', 'value': code, 'operation': operation,
            'receipt_sha256': digest(path), 'classification': result,
            'boundary': 'Current captured eligibility only; no CSV acceptance or import authority'}
