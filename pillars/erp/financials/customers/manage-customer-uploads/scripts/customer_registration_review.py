"""Bind supplied registration evidence to core preflight; never query or submit."""
from datetime import datetime
import json
from pathlib import Path
import re

import customers_package as package
from customer_campaign_review import context

require = package.require
TASK = 'ORA_AR_MANAGE_CUSTOMER_UPLOADS'
CONTRACT = Path(__file__).resolve().parents[1]/'assets/customer-registration-contract.json'


def positive_id(value):
    return isinstance(value, str) and re.fullmatch(r'[1-9][0-9]*', value) is not None


def timestamp(value):
    require(isinstance(value, str), 'REGISTRATION_CAPTURE_TIME')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise package.InvalidInput('REGISTRATION_CAPTURE_TIME') from exc
    require(parsed.tzinfo is not None, 'REGISTRATION_CAPTURE_TIME')
    return parsed


def parse_config(value):
    require(isinstance(value, str), 'REGISTRATION_CONFIG_TEXT_REQUIRED')
    def unique(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, 'REGISTRATION_CONFIG_DUPLICATE_KEY')
            result[key] = item
        return result
    def invalid_constant(_):
        raise package.InvalidInput('REGISTRATION_CONFIG_NONFINITE')
    try:
        result = json.loads(value, object_pairs_hook=unique, parse_constant=invalid_constant)
    except json.JSONDecodeError as exc:
        raise package.InvalidInput('REGISTRATION_CONFIG_JSON') from exc
    require(isinstance(result, dict), 'REGISTRATION_CONFIG_OBJECT')
    return result


def require_runtime_query_compatibility(config):
    """Check the reviewed 26D loader's lexical gate, not general SQL safety.

    FbdiProcessUtil.validateFbdiReadOnlyQuery rejects these tokens even inside
    string literals. Exact recipe matching remains mandatory after this check.
    Never rewrite supplied registration evidence to make it pass.
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if key == 'sql':
                require(isinstance(value, str), 'REGISTRATION_QUERY_RUNTIME_INCOMPATIBLE')
                normalized = value.strip()
                require(normalized.upper().startswith(('SELECT ', 'WITH '))
                    and not any(token in normalized for token in (';', '--', '/*', '*/')),
                    'REGISTRATION_QUERY_RUNTIME_INCOMPATIBLE')
            else:
                require_runtime_query_compatibility(value)
    elif isinstance(config, list):
        for value in config:
            require_runtime_query_compatibility(value)


def review_registration(candidate, operation, environment, evidence):
    """Review the customer recipe without consuming a core implementation format.

    This is business/deployment evidence only. It cannot establish core routing,
    approve a candidate, or replace the remaining execution gate.
    """
    checked = context(candidate, operation, environment)
    require(isinstance(evidence, dict) and set(evidence)=={'schema_version','environment_url',
        'captured_at','evidence_reference','complete','records'}, 'REGISTRATION_EVIDENCE_SCHEMA')
    require(evidence['schema_version']=='ar-customer-registration-evidence-v1'
        and evidence['environment_url']==environment, 'REGISTRATION_EVIDENCE_BINDING')
    timestamp(evidence['captured_at'])
    require(isinstance(evidence['evidence_reference'],str) and evidence['evidence_reference'].strip(),
            'REGISTRATION_PROVENANCE_REQUIRED')
    require(evidence['complete'] is True and isinstance(evidence['records'],list)
        and len(evidence['records'])==1, 'REGISTRATION_MISSING_INCOMPLETE_OR_AMBIGUOUS')
    expected = package.load_json(CONTRACT)
    row = evidence['records'][0]
    fields = expected['registration_fields']
    require(isinstance(row,dict) and set(row)==set(fields)|{
        'BUSINESS_OBJECT_ID','UI_BUSINESS_OBJECT_ID','LOAD_ADAPTER_CONFIG'}, 'REGISTRATION_RECORD_SCHEMA')
    require(all(positive_id(row[key]) for key in ('BUSINESS_OBJECT_ID','UI_BUSINESS_OBJECT_ID')),
            'REGISTRATION_RECORD_ID')
    require({key:row[key] for key in fields}==fields, 'REGISTRATION_METADATA_CHANGED')
    config = parse_config(row['LOAD_ADAPTER_CONFIG'])
    require_runtime_query_compatibility(config)
    # Canonical hashes distinguish JSON booleans from 0/1 and disregard only
    # insignificant JSON formatting. Unknown/changed config needs source review.
    require(package.fingerprint(config)==package.fingerprint(expected['adapter_config']),
            'REGISTRATION_RECIPE_CHANGED')
    normalized = {**row,'LOAD_ADAPTER_CONFIG':config}
    argument_recipe = {'application_id':row['APPLICATION_ID'],
        'interface_id':row['LOAD_ADAPTER_INTERFACE_ID'],
        'applicationArguments':config['applicationArguments'],
        'scopeResolver':config['loadExecution']['scopeResolver']}
    return {'schema_version': 'ar-customer-registration-business-review-v1',
        'status': 'SUPPLIED_REGISTRATION_RECIPE_MATCH',
        'candidate_sha256': checked['candidate_sha256'],
        'operation_intent': operation, 'environment_url': environment,
        'registration_sha256': package.fingerprint(normalized),
        'arguments_sha256': package.fingerprint(argument_recipe),
        'registration_evidence_sha256': package.fingerprint(evidence),
        'registration_contract_sha256': package.fingerprint(expected),
        'execution_authorized': False, 'live_ready': False,
        'core_routing_verified': False, 'approval_verified': False}


def analyze(candidate, operation, environment, core_envelope, evidence, runbook_control):
    checked = context(candidate, operation, environment)
    require(isinstance(core_envelope, dict) and set(core_envelope) == {
        'schemaVersion','preflight','fingerprint'} and core_envelope['schemaVersion']=='1.0',
        'REGISTRATION_CORE_ENVELOPE_SCHEMA')
    unsigned = {key:core_envelope[key] for key in ('schemaVersion','preflight')}
    require(core_envelope['fingerprint']==package.fingerprint(unsigned), 'REGISTRATION_CORE_ENVELOPE_CHANGED')
    preflight = core_envelope['preflight']
    require(isinstance(preflight, dict), 'REGISTRATION_CORE_PREFLIGHT')
    require(preflight.get('archiveSha256')==checked['candidate_sha256']
        and preflight.get('host')==environment and preflight.get('sourceType')=='FBDI'
        and preflight.get('taskRouted') is True and preflight.get('supportsRunBookTaskCode') is True
        and preflight.get('fbdiBusinessObject')=='customers'
        and preflight.get('fbdiUcmAccount')=='fin$/receivables$/import$'
        and preflight.get('fbdiLoadAdapterInterfaceId') in ('59',59)
        and preflight.get('fbdiFiles')==['ArUpdCustomers.csv'], 'REGISTRATION_CORE_ROUTE_MISMATCH')
    require(isinstance(runbook_control, dict) and runbook_control.get('mode')=='required'
        and runbook_control.get('status')=='active' and runbook_control.get('environment')==environment
        and positive_id(runbook_control.get('active_runbook_ref'))
        and preflight.get('runID')==runbook_control['active_runbook_ref'], 'REGISTRATION_RUNBOOK_BINDING')
    business = review_registration(candidate, operation, environment, evidence)
    binding = {'schema_version':'ar-customer-preflight-binding-v1',
        'candidate_sha256':checked['candidate_sha256'],'operation_intent':operation,
        'environment_url':environment,'task_code':TASK,
        'registration_sha256':business['registration_sha256'],
        'arguments_sha256':business['arguments_sha256'],
        'preflight_sha256':package.fingerprint(core_envelope),
        'registration_evidence_sha256':business['registration_evidence_sha256'],
        'registration_contract_sha256':business['registration_contract_sha256'],
        'runbook_control_sha256':package.fingerprint(runbook_control)}
    return {'schema_version':'ar-customer-registration-review-v1',
        'status':'SUPPLIED_REGISTRATION_AND_CORE_ROUTE_MATCH','binding':binding,
        'registration_captured_at':evidence['captured_at'],
        'final_data':{'archiveSha256':checked['candidate_sha256'],'customerFbdiBinding':binding},
        'execution_authorized':False,'live_ready':False,
        'limits':['Supplied evidence authenticity and freshness require source review.',
            'Arguments hash binds the scope/query recipe, not future request IDs or resolved argument values.',
            'No guarantee that server registration stays unchanged between capture and execution.',
            'Does not prove UCM privilege, field effects, Task Hook rule success or approval.']}


def preview_context(candidate, operation, environment, core_envelope, evidence, runbook_control, preview):
    """Extract acceptance context from an actual Task Hook preview after rules pass.

    Recompute from raw evidence; never accept a supplied pass report as authority.
    This does not authenticate supplied evidence and never creates an approval.
    """
    review = analyze(candidate, operation, environment, core_envelope, evidence, runbook_control)
    require(isinstance(preview,dict) and preview.get('taskCode')==TASK
        and preview.get('executionRoute')=='data-loader'
        and isinstance(preview.get('finalData'),dict), 'REGISTRATION_TASK_PREVIEW_REQUIRED')
    final = preview['finalData']
    require(final.get('archiveSha256')==review['final_data']['archiveSha256']
        and final.get('customerFbdiBinding')==review['binding'], 'REGISTRATION_PREVIEW_BINDING_CHANGED')
    require(timestamp(preview.get('generatedAt'))>=timestamp(review['registration_captured_at']),
            'REGISTRATION_PREVIEW_CAPTURE_ORDER')
    binding = review['binding']
    return {'environment_url':binding['environment_url'],
        'preview_id':package.fingerprint(preview),
        'registration_sha256':binding['registration_sha256'],
        'arguments_sha256':binding['arguments_sha256']}


def analyze_published(candidate, operation, environment, core_envelope, publication, live, runbook_control):
    """Bind a reviewed deployment to fresh core routing and the BO change marker.

    The full recipe is a retained deployment qualification, not a database query
    required on every implementor run. A later reported BO update requires new
    deployment review. This does not claim to have fetched the private recipe via REST.
    """
    review = analyze(candidate, operation, environment, core_envelope, publication, runbook_control)
    return _published_review(review, environment, publication, live)


def _published_review(review, environment, publication, live):
    require(isinstance(live, dict) and live.get('schema_version') == 'ar-customer-live-registration-v1'
        and live.get('environment_url') == environment and isinstance(live.get('evidence_reference'), str)
        and live['evidence_reference'].strip(), 'REGISTRATION_LIVE_EVIDENCE_SCHEMA')
    captured = timestamp(live.get('captured_at'))
    qualified = timestamp(publication['captured_at'])
    require(captured >= qualified, 'REGISTRATION_LIVE_CAPTURE_ORDER')
    pages = live.get('pages')
    require(isinstance(pages, list) and pages, 'REGISTRATION_LIVE_PAGES_REQUIRED')
    records, offset = [], 0
    for index, page in enumerate(pages):
        require(isinstance(page, dict) and isinstance(page.get('items'), list)
            and type(page.get('count')) is int and page['count'] == len(page['items'])
            and type(page.get('offset')) is int and page['offset'] == offset
            and type(page.get('hasMore')) is bool and page['hasMore'] == (index < len(pages)-1),
            'REGISTRATION_LIVE_PAGINATION_INCOMPLETE')
        require(all(isinstance(item, dict) for item in page['items']), 'REGISTRATION_LIVE_ITEM_SCHEMA')
        records.extend(item for item in page['items'] if item.get('BusObjTopDiscriminator') == 'customers'
                       or item.get('BusObjFileDiscriminator') == 'customers')
        offset += len(page['items'])
    require(len(records) == 1, 'REGISTRATION_LIVE_OBJECT_AMBIGUOUS_OR_MISSING')
    current, deployed = records[0], publication['records'][0]
    require(all(str(current.get(key)) == deployed[column] for key, column in {
        'BusinessObjectId': 'BUSINESS_OBJECT_ID', 'BusObjTopDiscriminator': 'BUS_OBJ_TOP_DISCRIMINATOR',
        'BusObjFileDiscriminator': 'BUS_OBJ_FILE_DISCRIMINATOR', 'ObjectType': 'OBJECT_TYPE',
        'ProductAreaCode': 'PRODUCT_AREA'}.items()), 'REGISTRATION_LIVE_OBJECT_CHANGED')
    modified = timestamp(current.get('LastUpdateDate'))
    require(modified <= qualified, 'REGISTRATION_CHANGED_SINCE_DEPLOYMENT_REVIEW')
    child = current.get('fbdiMetadata')
    require(isinstance(child, dict) and child.get('hasMore') is False and type(child.get('offset')) is int and child['offset'] == 0
        and isinstance(child.get('items'), list) and type(child.get('count')) is int
        and child['count'] == len(child['items']), 'REGISTRATION_LIVE_CHILD_INCOMPLETE')
    prefixes = []
    for entry in child['items']:
        require(isinstance(entry, dict), 'REGISTRATION_LIVE_CHILD_SCHEMA')
        expected = {'BusinessObjectId': deployed['BUSINESS_OBJECT_ID'], 'BusObjFileDiscriminator': 'customers',
            'ObjectType': 'FBDI', 'ApplicationId': '222', 'LoadAdapterInterfaceId': '59',
            'BusinessObject': 'customers', 'UcmAccount': 'fin/receivables/import', 'LoaderType': 'SQLLOADER'}
        require(all(str(entry.get(key)) == value for key, value in expected.items()), 'REGISTRATION_LIVE_ROUTE_CHANGED')
        prefixes.append(entry.get('DataFileNamePrefix'))
    expected_prefixes = parse_config(deployed['LOAD_ADAPTER_CONFIG'])['auxiliaryMetadata']['fileNamePrefixes']
    require(all(isinstance(p, str) for p in prefixes) and len(prefixes) == len(set(prefixes))
        and set(prefixes) == set(expected_prefixes), 'REGISTRATION_LIVE_PREFIXES_CHANGED')
    binding = {**review['binding'], 'live_registration_evidence_sha256': package.fingerprint(live)}
    return {**review, 'status': 'REVIEWED_DEPLOYMENT_AND_LIVE_CORE_ROUTE_MATCH', 'binding': binding,
        'registration_captured_at': live['captured_at'], 'deployment_qualified_at': publication['captured_at'],
        'server_recipe_read_live': False, 'reported_bo_change_since_qualification': False,
        'private_recipe_unchanged_proven': False,
        'final_data': {'archiveSha256': review['final_data']['archiveSha256'], 'customerFbdiBinding': binding},
        'limits': review['limits'] + ['Private recipe is the retained deployment qualification; fresh REST provides routing and LastUpdateDate only.',
            'The parent BO marker detects reported parent changes; it does not prove child/private recipe immutability or provide a transactional configuration lock.',
            'Deployment qualification and controlled registration changes remain separate from runtime routing; Data Loader resolves the registered recipe.',
            'A changed or unavailable marker requires deployment review, not an implementor SQL query or guessed recipe.']}


def published_preview_context(candidate, operation, environment, core_envelope, publication, live, runbook_control, preview):
    review = analyze_published(candidate, operation, environment, core_envelope, publication, live, runbook_control)
    require(isinstance(preview, dict) and preview.get('taskCode') == TASK and
        preview.get('executionRoute') == 'data-loader' and isinstance(preview.get('finalData'), dict),
        'REGISTRATION_TASK_PREVIEW_REQUIRED')
    require(preview['finalData'].get('archiveSha256') == review['final_data']['archiveSha256'] and
        preview['finalData'].get('customerFbdiBinding') == review['binding'], 'REGISTRATION_PREVIEW_BINDING_CHANGED')
    require(timestamp(preview.get('generatedAt')) >= timestamp(review['registration_captured_at']),
            'REGISTRATION_PREVIEW_CAPTURE_ORDER')
    return {'environment_url': environment, 'preview_id': package.fingerprint(preview),
        'registration_sha256': review['binding']['registration_sha256'],
        'arguments_sha256': review['binding']['arguments_sha256']}


def review_delegated_registration(candidate, operation, environment, publication, live,
                                  capability_evidence, runbook_control):
    """Customer-specific prerequisites, independent of core's approval protocol.

    Core still owns actual source capture, route resolution, approval and writes.
    This result is task evidence, never an emulated preflight/approval envelope.
    """
    import customer_loader_capability as capability
    business = review_registration(candidate, operation, environment, publication)
    required = capability.review(environment, capability_evidence)
    require(isinstance(runbook_control, dict) and runbook_control.get('mode') == 'required'
        and runbook_control.get('status') == 'active'
        and runbook_control.get('environment') == environment
        and positive_id(runbook_control.get('active_runbook_ref')), 'REGISTRATION_RUNBOOK_BINDING')
    binding = {key: business[key] for key in ('candidate_sha256', 'operation_intent',
        'environment_url', 'registration_sha256', 'arguments_sha256',
        'registration_evidence_sha256', 'registration_contract_sha256')}
    binding.update(schema_version='ar-customer-delegated-review-binding-v1',
        task_code=TASK, runbook_control_sha256=package.fingerprint(runbook_control),
        loader_capability_evidence_sha256=required['evidence_sha256'])
    base = {'binding': binding, 'final_data': {'archiveSha256': business['candidate_sha256']},
        'limits': ['Customer prerequisite evidence is not core approval or proof of executed routing.'],
        'execution_authorized': False, 'live_ready': False}
    result = _published_review(base, environment, publication, live)
    result['schema_version'] = 'ar-customer-delegated-registration-review-v1'
    result['status'] = 'CUSTOMER_REGISTRATION_PREREQUISITES_MATCH'
    result['core_route_verified'] = False
    result['core_decision_required'] = True
    return result
