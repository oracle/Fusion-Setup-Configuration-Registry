"""Plan a declared currency GET and classify captured pages; never performs I/O."""
from datetime import date
import re

FIELDS = ('CurrencyCode', 'CurrencyFlag', 'EnabledFlag', 'StartDateActive', 'EndDateActive')
PATH = '/fscmRestApi/resources/11.13.18.05/currenciesLOV'


def iso_day(value):
    if not isinstance(value, str) or re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) is None:
        raise ValueError('Explicit ISO date required')
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError('Explicit ISO date required')
    return result


def inputs(code, as_of):
    if not isinstance(code, str) or not code or code.strip() != code or not code.isascii() or len(code) > 15:
        raise ValueError('Explicit exact currency code of at most 15 ASCII characters required')
    return iso_day(as_of)


def request_plan(code, as_of, offset=0):
    inputs(code, as_of)
    # This is a query-serialization restriction, never an allowed product-code
    # catalog. Do not interpolate punctuation into the ADF query expression.
    if re.fullmatch(r'[A-Za-z0-9_.-]+', code) is None:
        raise ValueError('Declared lookup cannot safely represent this query literal; no currency-domain conclusion')
    if type(offset) is not int or offset < 0:
        raise ValueError('Nonnegative integer page offset required')
    return {'method': 'GET', 'path': PATH, 'query': {'q': "CurrencyCode='" + code + "'",
            'fields': ','.join(FIELDS), 'onlyData': 'true', 'limit': 100, 'offset': offset},
            'headers': {'REST-Framework-Version': '9'}, 'body': None,
            'currency_code': code, 'as_of': as_of, 'performs_network': False}


def classify(pages, code, as_of):
    day = inputs(code, as_of)
    unavailable = lambda reason: {'status': 'unavailable', 'reference_resolved': False,
        'failure_class': 'catalog_mismatch', 'reason': reason, 'performs_network': False}
    if not isinstance(pages, list) or not pages:
        return unavailable('Complete captured page sequence required')
    rows, expected_offset = [], 0
    for index, page in enumerate(pages):
        if not isinstance(page, dict) or not isinstance(page.get('items'), list):
            return unavailable('Expected collection response')
        batch = page['items']
        if (type(page.get('count')) is not int or page['count'] != len(batch)
                or type(page.get('offset')) is not int or page['offset'] != expected_offset
                or type(page.get('hasMore')) is not bool
                or page['hasMore'] != (index < len(pages) - 1)
                or page['hasMore'] and not batch):
            return unavailable('Incomplete, duplicated, out-of-order or inconsistent pages')
        if any(not isinstance(row, dict) or not set(FIELDS) <= set(row)
               or not isinstance(row['CurrencyCode'], str) for row in batch):
            return unavailable('Required response fields missing or malformed')
        rows.extend(batch)
        expected_offset += len(batch)
    matches = [row for row in rows if row['CurrencyCode'] == code]
    result = {'currency_code': code, 'as_of': as_of, 'exact_matches': len(matches),
              'reference_resolved': False, 'performs_network': False}
    if len(matches) != 1:
        result['status'] = 'not_found' if not matches else 'ambiguous'
        return result
    row = matches[0]
    if any(type(row[field]) is not str or row[field] not in {'Y', 'N'} for field in ['EnabledFlag', 'CurrencyFlag']):
        return unavailable('Unknown enabled/monetary flag encoding')
    try:
        start = None if row['StartDateActive'] is None else iso_day(row['StartDateActive'])
        end = None if row['EndDateActive'] is None else iso_day(row['EndDateActive'])
    except (TypeError, ValueError):
        return unavailable('Malformed active date')
    if start is not None and end is not None and end < start:
        return unavailable('Reversed active range')
    valid = row['EnabledFlag'] == 'Y' and row['CurrencyFlag'] == 'Y'
    valid = valid and (start is None or start <= day) and (end is None or day <= end)
    result.update(status='resolved' if valid else 'not_eligible_on_review_date', reference_resolved=valid)
    return result
