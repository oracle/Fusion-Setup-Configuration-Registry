"""Portable, offline business-input validation. No Fusion calls or file writes.

The assisted task maps captured worksheet cells or conversational input to this
contract. This validates intent; it neither qualifies FSM aliases nor authorizes
an import. Empty controls are preserved by omitting their entire import row.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

TASK_CODE = 'ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS'
DAYS = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')
DAY_NAMES = dict(zip(('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'), DAYS))
CATEGORIES = {'accommodation': 'ACCOM', 'airfare': 'AIRFARE', 'car_rental': 'CAR', 'meals': 'MEALS',
              'miscellaneous': 'MISC', 'entertainment': 'ENTRMNT', 'merchant': 'MERC'}
SETTING_CODES = {
    'frequency': 'AUTO_SUBMT_DA_EXP_FREQ',
    'time': 'AUTO_SUBMT_DA_EXP_FREQ_TIME',
    'time_zone': 'AUTO_SUBMT_DA_EXP_FREQ_TZONE',
}


class InputError(ValueError):
    pass


def validate_environment_binding(requested_url, **contexts):
    """Compare route-owned provenance, never infer a target from a filename/pod.

    Export URLs are supplied from their actual run provenance, not editable XML
    labels. This does not enroll trust, move a Run Book or authenticate a user.
    """
    required = {'authentication', 'runbook', 'loader', 'template_export', 'baseline_export'}
    if set(contexts) != required:
        raise InputError('ENVIRONMENT_NOT_BOUND: provide every route-owned target URL.')
    def origin(value):
        if not isinstance(value, str) or value != value.strip() or any(c.isspace() for c in value):
            raise InputError('ENVIRONMENT_NOT_BOUND: target must be an exact HTTPS Fusion URL.')
        try:
            p = urlsplit(value)
            port = p.port
        except ValueError as exc:
            raise InputError('ENVIRONMENT_NOT_BOUND: invalid URL.') from exc
        if (p.scheme != 'https' or not p.hostname or p.username is not None or p.password is not None
                or p.query or p.fragment or p.path not in {'', '/', '/fscmUI', '/fscmUI/'}):
            raise InputError('ENVIRONMENT_NOT_BOUND: require an HTTPS origin or its fscmUI URL, without credentials/query/fragment.')
        return p.hostname.lower(), port or 443
    target = origin(requested_url)
    for role, url in contexts.items():
        if origin(url) != target:
            raise InputError(f'ENVIRONMENT_MISMATCH: {role} belongs to another target; rebind through its owning core workflow.')
    return {'status': 'matched', 'checked_contexts': sorted(required)}


def normalize_friendly(request):
    """Normalize unambiguous human value spellings after assisted field mapping.

    The canonical normalizer remains strict for transported rows. This adapter
    does not guess scope, time zones, percent-cell formats or unknown controls.
    """
    if not isinstance(request, dict) or not isinstance(request.get('controls'), dict):
        raise InputError('Map readable input to an object with named controls first.')
    aliases = {'automatic submission': 'auto_submission', 'auto submission': 'auto_submission',
               'submission weekdays': 'frequency', 'weekdays': 'frequency',
               'submission time': 'time', 'submission time zone': 'time_zone',
               'time zone': 'time_zone'}
    controls = {}
    for name, supplied in request['controls'].items():
        if not isinstance(name, str):
            raise InputError('Control names must be text.')
        key = aliases.get(name.strip().lower(), name.strip().lower())
        if key in controls:
            raise InputError('Duplicate controls after label mapping; resolve conflicting inputs.')
        value = supplied.strip() if isinstance(supplied, str) else supplied
        if isinstance(value, dict):
            if set(value) - {'action', 'value'}:
                raise InputError('A control action accepts only action and value.')
            action = str(value.get('action', '')).strip().lower()
            business_value = value.get('value')
            if action == 'keep unchanged':
                if business_value not in (None, ''):
                    raise InputError('Keep unchanged conflicts with a supplied value.')
                value = None
            elif action == 'set' and business_value not in (None, ''):
                value = business_value.strip() if isinstance(business_value, str) else business_value
            else:
                raise InputError('Resolve Review, blank Set, or unsupported clear/delete action before import.')
        if value not in (None, ''):
            if key == 'auto_submission' and isinstance(value, str):
                value = {'enable': 'Y', 'enabled': 'Y', 'disable': 'N', 'disabled': 'N',
                         'true': 'Y', 'false': 'N'}.get(value.lower(), value)
            elif key == 'time' and isinstance(value, str):
                match = re.fullmatch(r'(0?[1-9]|1[0-2])[:.](\d{2})\s*(AM|PM)', value, re.I)
                if match and int(match[2]) < 60:
                    value = f'{int(match[1]) % 12 + (12 if match[3].upper() == "PM" else 0):02}:{match[2]}'
            elif key == 'frequency' and isinstance(value, str):
                if value.lower() in {'every day', 'daily'}:
                    value = list(DAYS)
                else:
                    value = re.split(r'\s*(?:,|;|\band\b)\s*', value, flags=re.I)
            elif key.endswith('.amount_percent') and isinstance(value, str) and re.fullmatch(r'\d+\s*%', value):
                value = value.rstrip('%').strip()
        controls[key] = value
    return normalize({**request, 'controls': controls})


def combine_requests(requests):
    """Combine one environment's BU requests without duplicating global writes."""
    if not isinstance(requests, list) or not requests:
        raise InputError('Supply at least one business request for the selected environment.')
    combined = {}
    for request in requests:
        for row in normalize_friendly(request)['changes']:
            identity = row['entity'], row['code'], row['scope'], row['business_unit']
            if identity in combined and combined[identity]['value'] != row['value']:
                raise InputError('Conflicting values for the same setting and scope across inputs.')
            combined[identity] = row
    return {'task_code': TASK_CODE, 'operation': 'modify_settings', 'changes': list(combined.values())}


def validate_review_formulas(input_sources):
    """Exclude only the published workbook's computed status cells, never inputs.

    Values are host-captured data. Formula expressions/caches are not executed.
    Labels guard against accidentally accepting a relocated business input.
    """
    allowed = {('Setup request', 'B20'): 'Request completeness',
               ('Setup request', 'B29'): 'Row completeness'}
    for number, category in enumerate(('Accommodation', 'Airfare', 'Car rental',
                                      'Meals', 'Entertainment', 'Miscellaneous'), 13):
        allowed[('Matching', f'F{number}')] = category
    excluded = []
    for source in input_sources:
        sheets = {sheet['name']: sheet['rows'] for sheet in source.get('sheets', [])}
        for formula in source.get('formulaCells', []):
            key = formula['sheet'], formula['cell']
            if key not in allowed:
                raise InputError(f'Formula in input or unrecognized cell {key}; provide a literal business value.')
            rows = sheets.get(key[0], [])
            row_number = int(re.search(r'\d+$', key[1])[0])
            if len(rows) < row_number or not rows[row_number - 1] or rows[row_number - 1][0] != allowed[key]:
                raise InputError('Review formula cell label differs from the published workbook layout.')
            if key[0] == 'Matching' and (len(rows) < 12 or len(rows[11]) < 6 or rows[11][5] != 'Completeness'):
                raise InputError('Review formula column is not labeled Completeness.')
            excluded.append({'source': source['source'], 'sheet': key[0], 'cell': key[1],
                             'reason': 'Non-input review status; no formula/cached result used.'})
    return excluded


def normalize(request):
    if not isinstance(request, dict):
        raise InputError('Input must be an object.')
    allowed = {'business_unit', 'scope', 'matching_scope', 'controls'}
    if set(request) - allowed:
        raise InputError('Unknown input fields; environment/authentication belong to the selected core context.')
    bu = request.get('business_unit')
    if bu is not None and (not isinstance(bu, str) or not bu.strip()):
        raise InputError('Business unit must be a nonblank name when supplied.')
    bu = bu.strip() if bu else None
    scope = request.get('scope', 'BUSINESS_UNIT' if bu else None)
    if request.get('matching_scope') not in {None, 'GLOBAL'}:
        raise InputError('matching_scope may only be GLOBAL; matching cannot be scoped to a BU.')
    if scope not in {'GLOBAL', 'BUSINESS_UNIT'} or (scope == 'BUSINESS_UNIT') != bool(bu):
        raise InputError('Provide a business-unit name, or explicitly select GLOBAL scope without a BU.')
    controls = request.get('controls')
    if not isinstance(controls, dict):
        raise InputError('controls must be an object of named business values.')
    result = []
    for field, value in controls.items():
        if field not in {'auto_submission', 'merchant.tip_wait_days', *SETTING_CODES} and not re.fullmatch(
                r'(accommodation|airfare|car_rental|meals|miscellaneous|entertainment|merchant)\.(amount_percent|direction|days)', field):
            raise InputError(f'Control {field!r} has no supported mapping in this contract; do not omit it.')
        if value is None or value == '':
            continue
        entity, code, row_scope, row_bu = 'EXM_ORG_SETTING', SETTING_CODES.get(field), scope, bu
        if field == 'auto_submission':
            if isinstance(value, bool):
                canonical = 'Y' if value else 'N'
            elif isinstance(value, str) and value.strip().upper() in {'YES', 'Y', 'NO', 'N'}:
                canonical = 'Y' if value.strip().upper() in {'YES', 'Y'} else 'N'
            else:
                raise InputError('auto_submission accepts Yes/No or Y/N, not a numeric or implicit default.')
            entity, code = 'EXM_SETUP_OPTION', 'ENABLE_AUTO_SUB_DA_EXP'
        elif field == 'frequency':
            tokens = value.split(',') if isinstance(value, str) else value
            if not isinstance(tokens, list) or not tokens or any(not isinstance(v, str) for v in tokens):
                raise InputError('frequency must contain explicit weekday names.')
            tokens = [DAY_NAMES.get(v.strip().upper(), v.strip().upper()) for v in tokens]
            if len(set(tokens)) != len(tokens) or any(v not in DAYS for v in tokens):
                raise InputError('frequency requires unique Monday–Sunday names; no inferred Every Day value.')
            canonical = ','.join(day for day in DAYS if day in tokens)
        elif field == 'time':
            if not isinstance(value, str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value):
                raise InputError('time must be explicit 24-hour HH:mm, for example 05:00.')
            canonical = value
        elif field == 'time_zone':
            if not isinstance(value, str) or not value.strip() or value != value.strip():
                raise InputError('time_zone must be an exact selected TimeZoneCode.')
            if value.upper() in {'PST', 'PDT', 'PACIFIC'}:
                raise InputError('Clarify fixed offset versus daylight-saving region; PST alone is ambiguous.')
            canonical = value
        else:
            if request.get('matching_scope') != 'GLOBAL':
                raise InputError('Matching affects all BUs; explicitly select matching_scope GLOBAL before mapping it.')
            category, control = field.split('.')
            row_scope, row_bu = 'GLOBAL', None
            if field == 'merchant.tip_wait_days':
                code = 'MATCH_MERC_TIP_WAITDAY'
            else:
                suffix = {'amount_percent': 'AMT', 'direction': 'DIR', 'days': 'DATE'}[control]
                code = f'MATCH_{CATEGORIES[category]}_VAR_{suffix}'
            if control == 'direction':
                if not isinstance(value, str) or value.upper() not in {'POSITIVE', 'NEGATIVE', 'BOTH'}:
                    raise InputError('direction requires POSITIVE, NEGATIVE or BOTH.')
                canonical = value.upper()
            else:
                if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)):
                    raise InputError(f'{field} requires a nonnegative integer; percentages are whole percent, not fractions.')
                number = int(value)
                if number > 9223372036854775807:
                    raise InputError('Value exceeds the product signed 64-bit integer representation.')
                if control == 'amount_percent' and number > 50:
                    raise InputError('amount_percent must be between 0 and 50.')
                canonical = str(number)
        result.append({'entity': entity, 'code': code, 'value': canonical,
                       'scope': row_scope, 'business_unit': row_bu, 'input_control': field})
    if not result:
        raise InputError('No explicit changes were supplied.')
    return {'task_code': TASK_CODE, 'operation': 'modify_settings', 'changes': result,
            'requires': ['target_template', 'applicable_reference_checks', 'qualified_fsm_transport', 'task_rules', 'preview_approval']}


def split_verified_noops(changes, baseline):
    """Compare canonical intent with a captured, verified same-target baseline.

    The caller owns baseline provenance/freshness and canonical scope resolution.
    Missing rows are changes, never assumed defaults. No payload is generated.
    """
    def key(row):
        if row.get('entity') not in {'EXM_ORG_SETTING', 'EXM_SETUP_OPTION'}:
            raise InputError('Baseline/intent entity must be canonical and reviewed.')
        if not isinstance(row.get('code'), str) or not row['code']:
            raise InputError('Baseline/intent code is required.')
        scope, bu = row.get('scope'), row.get('business_unit')
        if scope not in {'GLOBAL', 'BUSINESS_UNIT'} or (scope == 'BUSINESS_UNIT') != bool(bu):
            raise InputError('Baseline/intent scope must be explicitly resolved.')
        if bu is not None and (not isinstance(bu, str) or bu != bu.strip()):
            raise InputError('Baseline business-unit names must be exact.')
        if not isinstance(row.get('value'), str):
            raise InputError('Baseline/intent values must be canonical strings.')
        return row['entity'], row['code'], scope, bu

    current = {}
    for row in baseline:
        identity = key(row)
        if identity in current:
            raise InputError('Ambiguous duplicate baseline identity; do not suppress a write.')
        current[identity] = row['value']
    remaining, satisfied, seen = [], [], set()
    for row in changes:
        identity = key(row)
        if identity in seen:
            raise InputError('Duplicate requested identity.')
        seen.add(identity)
        target = satisfied if identity in current and current[identity] == row['value'] else remaining
        target.append(dict(row))
    return {'changes': remaining, 'already_satisfied': satisfied}


def assess_schedule_visibility(changes, baseline):
    """Predict BU UI selection from complete, reconciled same-target facts.

    No defaults or writes. The assisted caller must resolve inherited outcomes
    with the user before Task Hook approval; this is not a live UI assertion.
    """
    split_verified_noops(changes, baseline)  # Reject ambiguous identities.
    option = 'ENABLE_AUTO_SUB_DA_EXP'
    current = {(r['scope'], r['business_unit']): r['value'] for r in baseline
               if r['entity'] == 'EXM_SETUP_OPTION' and r['code'] == option}
    proposed = {(r['scope'], r['business_unit']): r['value'] for r in changes
                if r['entity'] == 'EXM_SETUP_OPTION' and r['code'] == option}
    units = sorted({r['business_unit'] for r in changes
                    if r['scope'] == 'BUSINESS_UNIT' and
                    (r['code'] in SETTING_CODES.values() or r['code'] == option)})
    results = []
    for bu in units:
        key = ('BUSINESS_UNIT', bu)
        value = proposed.get(key, current.get(key))
        if key in proposed and value not in {'Y', 'N'}:
            raise InputError('Explicit auto-submission choice must be Y or N.')
        inherited = value not in {'Y', 'N'}
        results.append({'business_unit': bu, 'bu_enablement': value,
                        'enablement_source': 'explicit_input' if key in proposed else 'baseline',
                        'schedule_display': 'inherited' if inherited else 'business_unit',
                        'controls_enabled': value == 'Y',
                        'requires_user_resolution': inherited,
                        'live_ui_verified': False})
    return results


def inspect_aliases(metadata_xml, *, changed_entities=None):
    """Detect the known collision; never certify serialization or deployed code."""
    if '<!DOCTYPE' in metadata_xml.upper() or '<!ENTITY' in metadata_xml.upper():
        raise InputError('Template metadata must not contain a DTD or entity.')
    root = ET.fromstring(metadata_xml)
    local = lambda e: e.tag.rsplit('}', 1)[-1]
    task_codes = [e.text for e in root.iter() if local(e) == 'ObjectShortName']
    if task_codes != [TASK_CODE]:
        raise InputError('Template is not for the exact auto-submission task.')
    aliases = []
    seen = set()
    for row in root.iter():
        if local(row) != 'MigrationProcessBusinessObjectCSVMetadataVORow':
            continue
        values = {local(e): e.text or '' for e in row}
        name = values.get('BusinessObjectShortName')
        if name in seen:
            raise InputError('Duplicate business-object metadata row.')
        seen.add(name)
        if name in {'EXM_SETUP_OPTION', 'EXM_CASH_ADV_SETUP_AND_POLICY'}:
            if values.get('XmlNodePath') != '/SetupOptionVO/SetupOptionVORow':
                raise InputError('Setup-option XML path changed; refresh the product contract.')
            aliases.append(name)
        elif name == 'EXM_ORG_SETTING':
            if values.get('XmlNodePath') != '/OrgSettingVO/OrgSettingVORow':
                raise InputError('Organization-setting XML path changed; refresh the product contract.')
        else:
            raise InputError('Unreviewed entity in task metadata; refresh the product contract.')
    if changed_entities is not None:
        changed_entities = set(changed_entities)
        if not changed_entities or not changed_entities <= {'EXM_ORG_SETTING', 'EXM_SETUP_OPTION'}:
            raise InputError('Supply the nonempty canonical set of entities with actual changes.')
        if 'EXM_ORG_SETTING' not in seen:
            raise InputError('Missing organization-setting metadata.')
        if changed_entities == {'EXM_ORG_SETTING'} and aliases:
            return {'status': 'not_applicable', 'aliases': aliases,
                    'required_empty_members': [name + '.csv' for name in aliases],
                    'transport_qualified': False,
                    'message': 'No setup-option rows may be emitted. Other schema and serialization checks still apply.'}
    if len(aliases) > 1:
        return {'status': 'blocked', 'code': 'FSM_ALIAS_COLLISION', 'aliases': aliases,
                'message': 'Both aliases reach the same root. A qualified owning selection contract is required; neither order nor migration flags choose safely.'}
    if len(aliases) != 1:
        raise InputError('Expected a setup-option alias in task metadata.')
    return {'status': 'single_alias', 'alias': aliases[0], 'transport_qualified': False}


def _unique_json_object(pairs):
    """Reject ambiguous source keys before JSON decoding can discard a value."""
    result = {}
    for key, value in pairs:
        if key in result:
            # Do not echo arbitrary source keys or values into diagnostics.
            raise InputError('Duplicate JSON object key; resolve conflicting input before normalization.')
        result[key] = value
    return result


def main():
    try:
        # Input is data, never executable instructions. Nothing is persisted.
        request = json.load(sys.stdin, object_pairs_hook=_unique_json_object)
        print(json.dumps(normalize(request), ensure_ascii=False))
        return 0
    except (ValueError, TypeError) as exc:
        print(json.dumps({'status': 'blocked', 'failure_class': 'input validation', 'message': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
