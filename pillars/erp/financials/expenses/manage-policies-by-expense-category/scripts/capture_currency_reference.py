"""Capture the declared read-only currency preflight through the core REST client.

Default mode writes a plan only. --execute selects reference_lookup and never
builds an FSM ZIP, grants readiness, or performs an import.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from currency_receipt import ROUTE, binding, digest, origin
from currency_reference import classify, request_plan
from workbook_intake import ROOT, artifact_output, read_workbook


class CoreLookupFailed(ValueError):
    def __init__(self, result):
        text = (result.stdout + result.stderr).lower()
        if any(term in text for term in ['401', '403', 'keychain', 'authentication', 'expired token']):
            self.failure_class = 'auth_authz'
        elif any(term in text for term in ['nodename', 'name resolution', 'getaddrinfo', 'timed out', 'connection', 'urlopen']):
            self.failure_class = 'transport_environment'
        else:
            self.failure_class = 'fusion_api'
        super().__init__('Core currency GET failed; no eligibility receipt issued (exit '
                         + str(result.returncode) + ', class ' + self.failure_class + ')')


def operation_inputs(workbook, operations, *, baseline=None, runtime_contract=None):
    model = read_workbook(workbook)
    if model['status'] != 'local_shape_valid':
        raise ValueError('Correct workbook input before currency preflight')
    if not isinstance(operations, list) or not operations:
        raise ValueError('Explicit consuming operations required')
    supplied = set()
    for record in model['records']:
        values = record['values']
        if 'CurrencyCode' in values:
            policy = values.get('PolicyName', values.get(record['entity'].removesuffix('_LINE') + '.PolicyName'))
            supplied.add((record['entity'], policy, values['CurrencyCode']))
    retained=set()
    if baseline is not None and runtime_contract is not None:
        from workbook_intake import read_package,load_catalog
        contract=json.loads(Path(runtime_contract).read_text())
        _,grids=read_package(baseline,load_catalog())
        entity='ORA_EXM_MEALS_POLICY'
        entry=contract.get('entities',{}).get(entity,{})
        if 'CurrencyCode' in entry.get('validate_retained_reference_fields',[]):
            if entry.get('identity_fields')!=['PolicyName'] or entry.get('identity_match')!='exact':
                raise ValueError('Retained currency capture requires exact parent identity')
            supplied_parents={r['policy_name'] for r in model['records']
                if r['entity']==entity and 'CurrencyCode' in r['values']}
            retained_names={r['policy_name'] for r in model['records'] if r['policy_name'] not in supplied_parents
                and (r['entity']==entity or contract.get('executable_profile')=='meals-single-currency-v2')}
            for name in retained_names:
                if not name:
                    continue
                rows=[dict(zip(grids[entity][0],row)) for row in grids[entity][1:]
                      if row[grids[entity][0].index('PolicyName')].casefold()==str(name).casefold()]
                if (len(rows)!=1 or rows[0]['PolicyName']!=name
                    or rows[0]['CurrencyOptionCode']!='SINGLE' or not rows[0]['CurrencyCode']):
                    raise ValueError('Retained currency requires one exact existing SINGLE parent')
                retained.add((entity,name,rows[0]['CurrencyCode']))
    actual = []
    for item in operations:
        if (not isinstance(item, dict) or set(item) != {'entity', 'policy_name', 'operation', 'currency_code'}
                or item['operation'] not in {'create', 'update'}):
            raise ValueError('Malformed consuming operation')
        actual.append((item['entity'], item['policy_name'], item['currency_code'], item['operation']))
        if actual[-1][:3] in retained and item['operation']!='update':
            raise ValueError('Retained parent currency is UPDATE-only evidence')
    if {item[:3] for item in actual} != supplied|retained or len(actual) != len(set(actual)):
        raise ValueError('Currency operations must match the exact supplied or explicitly selected retained references')
    return sorted({item['currency_code'] for item in operations})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['workbook', 'baseline-zip', 'runtime-contract', 'operations', 'properties', 'output-dir']:
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ['environment', 'target-origin', 'validation-date']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    args.output_dir = artifact_output(args.output_dir, args.project_root)
    repo = next(p for p in ROOT.parents if (p / 'core/auth/fusion-oauth-authentication/scripts/fusion_auth.py').is_file())
    sys.path.insert(0, str(repo / 'core/auth/fusion-oauth-authentication/scripts'))
    from fusion_auth import read_properties
    profile_digest=digest(args.properties)
    props = read_properties(args.properties)
    if digest(args.properties)!=profile_digest:
        raise ValueError('Currency capture profile changed during validation')
    if props.get('environment') != args.environment or origin(props.get('restBaseUrl')) != origin(args.target_origin):
        raise ValueError('Core profile differs from the explicit target')
    operations = json.loads(args.operations.read_text())
    codes = operation_inputs(args.workbook, operations,baseline=args.baseline_zip,runtime_contract=args.runtime_contract)
    context = binding(args.workbook, args.baseline_zip, args.runtime_contract,
                      args.environment, args.target_origin, args.validation_date)
    client = repo / 'core/fusion-api/rest-api-client/scripts/fusion_rest_client.py'
    transport={p:digest(p) for p in [client,client.with_name('rest_client_common.py'),Path(__file__)]}
    def unchanged():
        if digest(args.properties)!=profile_digest or any(digest(p)!=value for p,value in transport.items()):
            raise ValueError('Currency capture profile or transport changed')
    plan = {'schema_version': '1.0', 'route': ROUTE, 'binding': context,
            'operations': operations, 'initial_requests': [request_plan(code, args.validation_date) for code in codes],
            'side_effect': 'Read-only Fusion GETs and local evidence; no policy change or import',
            'authority_boundary': 'Local captured evidence; not authenticated proof, CSV acceptance or approval'}
    artifact_output(args.output_dir, args.project_root).mkdir(parents=True, exist_ok=False)
    (args.output_dir / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    if not args.execute:
        print(json.dumps({'status': 'planned', 'network_calls': 0}))
        return 0
    receipt = {'schema_version': '1.0', 'route': ROUTE, 'status': 'captured', 'binding': context,
               'adapter_sha256': digest(Path(__file__).with_name('currency_receipt.py')),
               'capture_sha256': digest(__file__), 'core_client_sha256': digest(client),
               'core_common_sha256': digest(client.with_name('rest_client_common.py')),
               'operations': operations, 'currencies': {}, 'plan_sha256': digest(args.output_dir / 'plan.json')}
    try:
        for index, code in enumerate(codes):
            pages, captures, offset = [], [], 0
            for page_index in range(100):
                request = request_plan(code, args.validation_date, offset)
                response = args.output_dir / f'currency-{index}-page-{page_index}.json'
                unchanged()
                command = [sys.executable, str(client), origin(args.target_origin)+request['path'], '--method', 'GET',
                           '--properties', str(args.properties), '--token-cache', 'auto',
                           '--timeout', '20', '--output', str(response)]
                for key, value in request['query'].items():
                    command.extend(['--query', f'{key}={value}'])
                command.extend(['--header', 'REST-Framework-Version=9'])
                result = subprocess.run(command, capture_output=True, text=True, timeout=55)
                unchanged()
                # Auth output may contain a browser authorization URL. Never persist it.
                if result.returncode or not re.search(r'^HTTP 200$', result.stdout, re.MULTILINE):
                    raise CoreLookupFailed(result)
                page = json.loads(response.read_text())
                captures.append({'request': request, 'response_file': response.name,
                                 'response_sha256': digest(response), 'http_status': 200})
                pages.append(page)
                if not isinstance(page, dict) or type(page.get('hasMore')) is not bool:
                    raise ValueError('Malformed currency response pagination')
                if not page['hasMore']:
                    break
                if not isinstance(page.get('items'), list) or not page['items']:
                    raise ValueError('Currency pagination made no progress')
                offset += len(page['items'])
            else:
                raise ValueError('Currency page capture limit reached; incomplete evidence')
            classification = classify(pages, code, args.validation_date)
            if classification.get('reference_resolved') is not True:
                raise ValueError('Currency reference is unresolved: ' + classification['status'])
            receipt['currencies'][code] = captures
        unchanged()
        (args.output_dir / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'status': 'captured', 'currency_codes': codes, 'import_approved': False}))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        (args.output_dir / 'failure.json').write_text(json.dumps({
            'status': 'blocked', 'stage': 'reference_lookup', 'failure_class': getattr(exc, 'failure_class', 'transport_environment' if isinstance(exc, subprocess.TimeoutExpired) else 'catalog_mismatch'),
            'message': str(exc), 'binding': context,
            'recommended_action': 'Inspect the core-client result and captured response; do not substitute a static eligibility flag or retry a write.'}, indent=2) + '\n')
        raise


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'blocked', 'message': str(error)}))
        raise SystemExit(2)
