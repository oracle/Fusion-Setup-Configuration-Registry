"""Check exact account existence and classify interest accounts using COA configuration and live LOVs.

Never infer absence or configuration from a SOAP rejection. No writes are made.
"""
from __future__ import annotations
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import urllib.parse
import zipfile
from xml.etree import ElementTree
from typing import Any

from interest_account_validation import parse_segments
sys.path.insert(0, str(Path(__file__).resolve().parents[6] / 'core/data-loader/scripts'))
import data_loader_metadata as metadata

INSTANCE = 'ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_INSTANCE.csv'
SEGMENT = 'ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_SEGMENT.csv'
TASK_CODE = 'GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES'
FIXED_FIELDS = frozenset(('AccountType','JgzzReconFlag','DetailBudgetingAllowedFlag','FinancialCategory',
    'Reference5','Reference3','DetailPostingAllowedFlag','Reference4','SummaryFlag','StartDateActive',
    'EndDateActive','EnabledFlag','_CODE_COMBINATION_ID','_CHART_OF_ACCOUNTS_ID','@context','links'))


class ResolutionError(RuntimeError):
    """Evidence cannot support an account classification or creation choice."""


def _existing_account_message(failure: dict[str, Any]) -> str:
    """Explain the account restriction; retain technical diagnostics separately."""
    codes = set(failure.get('errorCodes', []))
    reasons = []
    if 'GL_ACCT_COMB_DIS_ACCT' in codes:
        reasons.append('is disabled')
    if 'GL_ASM_ACCOUNT_EXPIRED' in codes:
        reasons.append('is not currently active because of its start or end date')
    if 'GL_ASM_ACCOUNT_POSTING' in codes:
        reasons.append('does not allow posting')
    if reasons:
        return 'This account exists but ' + '; it '.join(reasons) + '. Please choose another account.'
    reason = failure.get('message')
    return ('This account exists, but it could not be validated for use. '
            + (reason + ' ' if reason else '') + 'Please choose another account.')


def _one(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    if len(rows) != 1:
        raise ResolutionError(f'{label} must have exactly one exact match.')
    return rows[0]


def _get(config: dict[str, Any], resource: str, q: str, *, offset: int = 0) -> dict[str, Any]:
    url = config['host'] + '/fscmRestApi/resources/11.13.18.05/' + resource + '?' + urllib.parse.urlencode(
        {'q': q, 'onlyData': 'true', 'limit': 500, 'offset': offset, 'totalResults': 'true'})
    return metadata.get_json(url, config['auth'], stage='Invoice Options account existence/configuration check')


def _page(value: Any, offset: int) -> tuple[list[dict[str, Any]], bool]:
    if (not isinstance(value, dict) or not isinstance(value.get('items'), list)
            or len(value['items']) > 500 or any(not isinstance(x, dict) for x in value['items'])
            or type(value.get('hasMore')) is not bool
            or type(value.get('offset')) is not int or value['offset'] != offset
            or type(value.get('count')) is not int or value['count'] != len(value['items'])
            or (value['hasMore'] and not value['items'])):
        raise ResolutionError('Incomplete or malformed account lookup pagination; existence is unknown.')
    return value['items'], value['hasMore']


def _configuration(path: Path, baseline: Any, chart: dict[str, Any]) -> tuple[dict[str, str], list[dict[str, str]], str]:
    try:
        data = path.read_bytes()
        if len(data) > 32 * 1024 * 1024:
            raise ResolutionError('COA configuration export is too large.')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos = z.infolist()
            if (len(infos) > 100 or len({x.filename for x in infos}) != len(infos)
                    or sum(x.file_size for x in infos) > 64 * 1024 * 1024
                    or any(x.flag_bits & 1 or x.file_size > 16 * 1024 * 1024 for x in infos)):
                raise ResolutionError('Unsafe or oversized COA export.')
            xml = z.read('ASM_SETUP_CSV_METADATA.xml')
            if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper() or b'\x00' in xml:
                raise ResolutionError('Unsupported COA metadata XML.')
            root = ElementTree.fromstring(xml)
            def field(name):
                matches = [x.text or '' for x in root.iter() if x.tag.rsplit('}',1)[-1] == name]
                return matches[0] if len(matches) == 1 else ''
            if (field('ObjectShortName') != TASK_CODE or field('ProcessStatus') != 'COMPLETED'
                    or field('ProcessType') != 'EXPORT' or field('ProcessEnv') != baseline.metadata['ProcessEnv']
                    or field('ProcessRelease') != baseline.metadata['ProcessRelease']):
                raise ResolutionError('COA export task, environment, release or completion does not match this baseline.')
            observed = dt.datetime.fromisoformat(field('ProcessEndDate').replace('Z', '+00:00'))
            if observed.utcoffset() is None:
                # Native Fusion exports may omit the timezone. Do not assign one:
                # freshness can instead come from the observed new export run.
                observation_path = path.with_name(path.name + '.observation.json')
                try:
                    observation = json.loads(observation_path.read_text(encoding='utf-8'))
                    def instant(name):
                        value = dt.datetime.fromisoformat(observation[name].replace('Z', '+00:00'))
                        if value.utcoffset() is None:
                            raise ValueError('Observation needs a timezone.')
                        return value.astimezone(dt.timezone.utc)
                    started, completed, seen = [instant(k) for k in ('startedAt', 'completedAt', 'observedAt')]
                    now = dt.datetime.now(dt.timezone.utc)
                    if (observation.get('schemaVersion') != 'invoice-coa-export-observation-v1'
                            or observation.get('source') != 'shared.setup-export.task-level-export'
                            or observation.get('taskCode') != TASK_CODE
                            or observation.get('status') != 'COMPLETED'
                            or observation.get('processCompletedFlag') is not True
                            or not re.fullmatch(r'[1-9][0-9]*', str(observation.get('processId', '')))
                            or observation.get('artifactSha256') != hashlib.sha256(data).hexdigest()
                            or observation.get('environment') != field('ProcessEnv')
                            or observation.get('release') != field('ProcessRelease')
                            or not now-dt.timedelta(hours=24) <= started <= completed <= seen <= now+dt.timedelta(seconds=300)):
                        raise ValueError('Export observation is stale or does not match this ZIP.')
                    observed = started
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    raise ResolutionError('COA export has no timezone. Obtain a fresh export with export_interest_account_configuration.py and retain its matching observation receipt.') from exc
            observed = observed.astimezone(dt.timezone.utc)
            age = (dt.datetime.now(dt.timezone.utc)-observed).total_seconds()
            if not -300 <= age <= 86400:
                raise ResolutionError('COA configuration export is stale or future-dated; obtain a fresh export.')
            def rows(name):
                reader = csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig')))
                headers = reader.fieldnames
                if not headers or len(headers) != len(set(headers)):
                    raise ResolutionError('Malformed COA CSV headers.')
                result = list(reader)
                if any(None in row or any(v is None for v in row.values()) for row in result):
                    raise ResolutionError('Malformed COA CSV rows.')
                return [r for r in result if r.get('FND_APP_KEY_FLEXFIELD.KeyFlexfieldCode') == 'GL#'
                        and r.get('FND_APP_KEY_FLEXFIELD.ApplicationId') == '101']
            instance = _one([r for r in rows(INSTANCE) if r.get('StructureInstanceCode') == chart.get('StructureInstanceCode')], 'Exported COA instance')
            segments = [r for r in rows(SEGMENT) if r.get('KEY_FLEXFIELD_STRUCTURE.StructureCode') == instance.get('StructureCode') and r.get('EnabledFlag') == 'Y']
    except (OSError, KeyError, ValueError, zipfile.BadZipFile, ElementTree.ParseError, RuntimeError) as exc:
        if isinstance(exc, ResolutionError):
            raise
        raise ResolutionError('Cannot read a complete matching COA configuration export.') from exc
    columns = [r.get('ColumnName','') for r in segments]
    if (not segments or len(columns) != len(set(columns))
            or any(not re.fullmatch(r'SEGMENT(?:[1-9]|[12][0-9]|30)', c) for c in columns)):
        raise ResolutionError('COA physical segment mapping is incomplete or ambiguous.')
    return instance, sorted(segments, key=lambda r: int(r['ColumnName'][7:])), hashlib.sha256(data).hexdigest()


def _normalized(value: str) -> str:
    # Fusion encodes punctuation in dynamic attribute names, e.g. Sub_2DAccount.
    value = re.sub(r'_([0-9][0-9A-Fa-f])', lambda m: chr(int(m[1],16)), value)
    return re.sub('[^a-z0-9]', '', value.casefold())


def _mapping(row: dict[str, Any], segments: list[dict[str, str]]) -> list[str]:
    keys = set(row)-FIXED_FIELDS
    mapped = []
    for segment in segments:
        key = None
        for field in ('SegmentCode','Name','ColumnName'):
            wanted = segment.get(field,'')
            if not wanted:
                continue
            matches = [k for k in keys if _normalized(k) == _normalized(wanted)]
            if len(matches) > 1:
                raise ResolutionError('Account LOV segment mapping is ambiguous.')
            if matches:
                key = matches[0]
                break
        if key is None or key in mapped:
            raise ResolutionError('Account LOV does not expose a complete unique segment mapping.')
        mapped.append(key)
    if set(mapped) != keys:
        raise ResolutionError('Account LOV dynamic fields differ from the exported COA segments.')
    return mapped


def lookup_account(config, baseline, ledger, account):
    """Complete exact account lookup before deciding whether creation is applicable."""
    path = config.get('coaConfiguration')
    if not path:
        raise ResolutionError('A fresh matching COA configuration export is required to check account existence.')
    escaped = ledger.replace("'", "''")
    rows, more = _page(_get(config,'ledgersLOV',f"Name='{escaped}'"),0)
    if more:
        raise ResolutionError('Ledger lookup is incomplete.')
    ledger_row = _one([r for r in rows if r.get('Name') == ledger], 'Ledger')
    coa = str(ledger_row.get('ChartOfAccountsId',''))
    if not re.fullmatch(r'[1-9][0-9]*',coa):
        raise ResolutionError('Ledger chart of accounts is unresolved.')
    rows, more = _page(_get(config,'chartOfAccountsLOV',f"StructureInstanceNumber='{coa}'"),0)
    if more:
        raise ResolutionError('COA lookup is incomplete.')
    chart = _one([r for r in rows if str(r.get('StructureInstanceNumber')) == coa], 'COA')
    instance, segments, digest = _configuration(Path(path),baseline,chart)
    slots = parse_segments(account)
    indexes = [int(s['ColumnName'][7:])-1 for s in segments]
    # Compare complete positional vectors for existence. Do not decide whether
    # supplied slots/values are eligible: Fusion validates those on submission.
    expected = slots + [''] * (30 - len(slots))
    matches = []; seen = set(); offset=0; pages=0
    for _ in range(100):
        rows, more = _page(_get(config,'accountCombinationsLOV',f'_CHART_OF_ACCOUNTS_ID={coa}',offset=offset),offset)
        for row in rows:
            ccid = str(row.get('_CODE_COMBINATION_ID',''))
            if str(row.get('_CHART_OF_ACCOUNTS_ID')) != coa or not re.fullmatch(r'[1-9][0-9]*',ccid) or ccid in seen:
                raise ResolutionError('Account lookup returned inconsistent COA or duplicate account identities.')
            seen.add(ccid)
            values = ['' if row[k] is None else row[k] for k in _mapping(row,segments)]
            if any(not isinstance(v,str) for v in values):
                raise ResolutionError('Account LOV contains incomplete segment values.')
            row_slots = [''] * 30
            for index, value in zip(indexes, values, strict=True):
                row_slots[index] = value
            if row_slots == expected:
                matches.append(ccid)
        offset += len(rows);pages += 1
        if not more:
            break
    else:
        raise ResolutionError('Account lookup exceeded its bound; absence is unconfirmed.')
    proof = {'chartOfAccountsId':coa,'structureInstanceCode':chart['StructureInstanceCode'],
             'configurationSha256':digest,'rowsChecked':offset,'pagesChecked':pages,'lookupComplete':True,
             'exactMatches':matches,'dynamicCombinationCreationAllowed':instance.get('DynamicCombinationCreationAllowed')}
    return proof, instance, chart


def diagnose_account(config: dict[str, Any], baseline: Any, ledger: str, account: str, response: dict[str, Any]) -> dict[str, Any]:
    failure = response.get('validationFailure') or {}
    if failure.get('classification') != 'invalid_account':
        return {'classification':'validation_unavailable', 'creationAllowed':False,
                'message':'The account check failed. I cannot tell whether this account exists. Please resolve the service error and try again.'}
    if 'GL_ADFDI_SEGMENT_NOTEXIST' in failure.get('errorCodes', []):
        return {'classification':'segment_rejected_by_fusion', 'creationAllowed':False,
                'message': 'A segment value was rejected: ' + failure.get('message', 'A supplied segment value does not exist.')
                           + ' Please provide a corrected account. Creating a combination will not create the missing segment value.'}
    proof, instance, chart = lookup_account(config, baseline, ledger, account)
    matches = proof['exactMatches']
    return classify_account(proof, instance, chart, failure)


def classify_account(proof, instance, chart, failure):
    matches = proof['exactMatches']
    if matches:
        return {**proof,'classification':'existing_unusable','creationAllowed':False,
                'message':_existing_account_message(failure)}
    if set(failure.get('errorCodes', [])) & {'GL_ACCT_COMB_DIS_ACCT', 'GL_ASM_ACCOUNT_EXPIRED', 'GL_ASM_ACCOUNT_POSTING'}:
        return {**proof, 'classification':'account_evidence_conflict','creationAllowed':False,
                'message':'Fusion reported an account usage restriction, but the lookup did not find the account. I cannot confirm absence. Please resolve the account or access issue before continuing.'}
    if proof['rowsChecked'] == 0:
        raise ResolutionError('No accounts were visible for this COA; absence cannot be established.')
    flag = instance.get('DynamicCombinationCreationAllowed')
    if flag == 'N':
        return {**proof,'classification':'missing_creation_disabled','creationAllowed':False,
                'message':'This account combination does not exist. Dynamic creation is disabled for this chart of accounts. Please choose an existing account or ask your administrator to review the setting.'}
    if (flag != 'Y' or instance.get('EnabledFlag') != 'Y' or chart.get('EnabledFlag') not in (True,'Y')):
        return {**proof,'classification':'missing_configuration_unknown','creationAllowed':False,
                'message':'This account combination does not exist, but I could not confirm that creation is allowed. No account will be created. Please review the chart-of-accounts configuration.'}
    return {**proof,'classification':'missing_creation_available','creationAllowed':True,
            'choices':['create','use_existing','stop'],
            'message':'This account combination does not exist, and dynamic creation is enabled for this chart of accounts. Do you want to create this combination, use an existing account, or stop? Fusion will validate the combination rules when creation is attempted. Nothing has been created.'}
