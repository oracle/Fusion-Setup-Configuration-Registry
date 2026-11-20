"""Associate a retained Customers attempt with core's read-only status result."""
import re
from urllib.parse import urlsplit

import customers_package as package
from customer_request_review import timestamp

TASK = 'ORA_AR_MANAGE_CUSTOMER_UPLOADS'
DEFINITIONS = {
    'initiation': 'JobDefinition://oracle/apps/ess/hcm/common/dataLoader/HRC_DL_MAIN',
    'interface': 'JobDefinition://oracle/apps/ess/financials/commonModules/shared/common/interfaceLoader/InterfaceLoaderController',
    'product': 'JobDefinition://oracle/apps/ess/financials/receivables/customerSetup/customerProfileClasses/UploadCustomerEss',
}
require = package.require


def identifier(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    value = str(value)
    return value if re.fullmatch(r'[1-9][0-9]*', value) else None


def analyze(candidate, operation, environment_url, binding, observation):
    observation_hash = package.fingerprint(observation)
    # Task-owned REST capture is distinguished from historical native core output.
    if isinstance(observation, dict) and observation.get('schema_version') == 'ar-customer-task-status-evidence-v1':
        require(set(observation) == {'schema_version', 'binding_sha256', 'environment_url',
                'captured_at', 'evidence_reference', 'task_status'}, 'ATTEMPT_OBSERVATION_SCHEMA')
        observation = dict(observation)
        observation['core_status'] = observation.pop('task_status')
        observation['schema_version'] = 'ar-customer-core-status-evidence-v1'
    preview = package.inspect_candidate(candidate, operation)
    origin = urlsplit(environment_url)
    require(origin.scheme == 'https' and origin.hostname and not origin.username
            and not origin.password and origin.path in ('', '/') and not origin.query
            and not origin.fragment, 'ATTEMPT_ENVIRONMENT')
    require(isinstance(binding, dict), 'ATTEMPT_BINDING_SCHEMA')
    version = binding.get('schema_version')
    require(version in ('ar-customer-runtime-binding-v1',
                        'ar-customer-runtime-binding-v2'), 'ATTEMPT_BINDING_VERSION')
    # These hashes identify retained evidence, not an approval capability.
    # v1 remains readable for historical attempts; v2 does not require core
    # to export its private execution plan or emulate an old preflight file.
    context_hashes = ('preflight_sha256',) if version.endswith('-v1') else (
        'customer_review_sha256', 'core_evidence_sha256')
    require(set(binding) == {
        'schema_version', 'candidate_sha256', 'environment_url', 'operation_intent',
        'registration_sha256', 'arguments_sha256',
        'initiation_request_id', 'content_id', 'run_id', 'task_code', 'initiated_at',
        'initiation_evidence_reference'} | set(context_hashes), 'ATTEMPT_BINDING_SCHEMA')
    require(binding['candidate_sha256'] == preview['candidate_sha256']
            and binding['environment_url'] == environment_url
            and binding['operation_intent'] == operation and binding['task_code'] == TASK,
            'ATTEMPT_BINDING_MISMATCH')
    require(all(isinstance(binding[k], str) and re.fullmatch(r'[0-9a-f]{64}', binding[k])
                for k in ('registration_sha256', 'arguments_sha256') + context_hashes),
            'ATTEMPT_CONTEXT_HASH')
    require(all(isinstance(binding[k], str) and identifier(binding[k]) for k in
                ('initiation_request_id', 'run_id')), 'ATTEMPT_BINDING_ID')
    require(isinstance(binding['content_id'], str) and re.fullmatch(r'UCMFA[0-9]+', binding['content_id']),
            'ATTEMPT_CONTENT_ID')
    require(isinstance(binding['initiation_evidence_reference'], str)
            and binding['initiation_evidence_reference'].strip(), 'ATTEMPT_PROVENANCE')
    require(isinstance(observation, dict) and set(observation) == {
        'schema_version', 'binding_sha256', 'environment_url', 'captured_at',
        'evidence_reference', 'core_status'}, 'ATTEMPT_OBSERVATION_SCHEMA')
    require(observation['schema_version'] == 'ar-customer-core-status-evidence-v1', 'ATTEMPT_OBSERVATION_VERSION')
    require(observation['binding_sha256'] == package.fingerprint(binding)
            and observation['environment_url'] == environment_url, 'ATTEMPT_OBSERVATION_BINDING')
    require(timestamp(observation['captured_at']) >= timestamp(binding['initiated_at']), 'ATTEMPT_CAPTURE_TIME')
    require(isinstance(observation['evidence_reference'], str)
            and observation['evidence_reference'].strip(), 'ATTEMPT_PROVENANCE')
    core = observation['core_status']
    require(not isinstance(core, dict) or 'fbdiDiagnostics' in core,
            'ATTEMPT_CENTRAL_DIAGNOSTICS_CONTRACT_REQUIRED')
    require(isinstance(core, dict) and isinstance(core.get('dataSets'), list)
            and isinstance(core.get('fbdiDiagnostics'), list), 'ATTEMPT_CORE_SCHEMA')
    findings = []
    lookup_matches = (core.get('RequestId') == binding['initiation_request_id']
                      or core.get('UcmContentId') == binding['content_id'])
    if (not lookup_matches or ('RequestId' in core and core['RequestId'] != binding['initiation_request_id'])
        or ('UcmContentId' in core and core['UcmContentId'] != binding['content_id'])):
        findings.append('CORE_LOOKUP_MISMATCH')
    datasets = core['dataSets']
    require(all(isinstance(row, dict) for row in datasets), 'ATTEMPT_DATASET_SCHEMA')
    stage_ids = None
    interface_failure = None
    if len(datasets) != 1 or type(core.get('dataSetCount')) is not int or core['dataSetCount'] != len(datasets):
        findings.append('DATASET_MISSING_OR_AMBIGUOUS')
    else:
        dataset = datasets[0]
        dataset_id = identifier(dataset.get('DataSetId'))
        if core.get('queriedDataSetIds') != [dataset_id]:
            findings.append('QUERIED_DATASET_SCOPE_MISMATCH')
        if not dataset_id:
            findings.append('DATASET_ID_INVALID')
        if (dataset.get('SourceType') != 'FBDI'
            or identifier(dataset.get('DataSetRequestId')) != binding['initiation_request_id']
            or dataset.get('UcmContentId') != binding['content_id']
            or identifier(dataset.get('RunId')) != binding['run_id']
            or dataset.get('RunTaskCode') != TASK):
            findings.append('DATASET_CONTEXT_MISMATCH')
        diagnostics = core['fbdiDiagnostics']
        require(all(isinstance(d, dict) for d in diagnostics), 'ATTEMPT_DIAGNOSTIC_SCHEMA')
        if len(diagnostics) != 1 or diagnostics[0].get('dataSetId') != dataset_id:
            findings.append('DIAGNOSTIC_SCOPE_MISSING_OR_AMBIGUOUS')
        else:
            diagnostic = diagnostics[0]
            if diagnostic.get('collectionComplete') is not True or diagnostic.get('sectionErrors'):
                findings.append('DIAGNOSTICS_INCOMPLETE')
            objects = diagnostic.get('businessObjects')
            require(isinstance(objects, list) and all(isinstance(row, dict) and isinstance(row.get('record'), dict)
                    for row in objects), 'ATTEMPT_OBJECT_SCHEMA')
            if len(objects) != 1 or objects[0]['record'].get('BusinessObjectName') != 'customers':
                findings.append('BUSINESS_OBJECT_MISMATCH_OR_AMBIGUOUS')
            processes = diagnostic.get('processes')
            require(isinstance(processes, list) and all(isinstance(row, dict) for row in processes),
                    'ATTEMPT_PROCESS_SCHEMA')
            ids = [identifier(row.get('ProcessId')) for row in processes]
            if None in ids or len(ids) != len(set(ids)):
                findings.append('PROCESS_IDS_INVALID_OR_DUPLICATED')
            if any(identifier(row.get('DataSetId')) != dataset_id for row in processes):
                findings.append('PROCESS_DATASET_MISMATCH')
            selected = {}
            for stage, definition in DEFINITIONS.items():
                matches = [row for row in processes if row.get('Definition') == definition]
                if len(matches) != 1:
                    findings.append(stage.upper() + '_PROCESS_MISSING_OR_AMBIGUOUS')
                else:
                    selected[stage] = identifier(matches[0].get('ProcessId'))
            if selected.get('initiation') != binding['initiation_request_id']:
                findings.append('INITIATION_PROCESS_MISMATCH')
            if not findings:
                stage_ids = selected
            elif findings == ['PRODUCT_PROCESS_MISSING_OR_AMBIGUOUS'] and len(processes) == 2:
                # Recognize only a fully scoped, terminal interface failure.
                # Preserve the three-stage association contract: no product ID
                # is invented and staging_attempt must still reject this case.
                by_role = {role: [row for row in processes if row.get('Definition') == definition]
                           for role, definition in DEFINITIONS.items()}
                record = objects[0]['record']
                if (not by_role['product']
                    and len(by_role['initiation']) == len(by_role['interface']) == 1
                    and all(by_role[role][0].get('Status') in ('Error', 'ERROR')
                            for role in ('initiation', 'interface'))
                    and record.get('ImportStatusCode') == 'ERROR'
                    and record.get('LoadStatusCode') == 'UNPROCESSED'):
                    interface_failure = {'initiation_request_id': selected['initiation'],
                                         'interface_request_id': selected['interface'],
                                         'product_process_observed': False,
                                         'import_status': 'ERROR', 'load_status': 'UNPROCESSED'}
    return {'schema_version': 'ar-customer-attempt-review-v1',
            'status': ('STAGE_IDS_ASSOCIATED' if not findings else
                       'INTERFACE_FAILURE_NO_PRODUCT_OBSERVED' if interface_failure else 'ASSOCIATION_INCOMPLETE'),
            'binding_sha256': package.fingerprint(binding),
            'observation_sha256': observation_hash,
            'findings': findings, 'stage_request_ids': stage_ids,
            'interface_failure_observation': interface_failure,
            'request_association_matches': not findings,
            'candidate_staging_lineage_verified': False, 'persisted_reconciliation_complete': False,
            'execution_authorized': False, 'retry_authorized': False, 'journey_complete': False,
            'limits': ['Supplied evidence is not authenticated by this offline helper.',
                       'Metadata association does not prove product argument values or staging/persisted results.',
                       'Process status and ESS parent/root IDs are never used to infer success or request role.',
                       'Multiple datasets or matching product processes require explicit scope review.']}


def staging_attempt(candidate, operation, environment_url, binding, observation):
    """Create the existing staging-review input only after exact association."""
    result = analyze(candidate, operation, environment_url, binding, observation)
    require(result['request_association_matches'], 'ATTEMPT_ASSOCIATION_INCOMPLETE')
    ids = result['stage_request_ids']
    return {'schema_version': 'ar-customer-request-attempt-v1',
            'candidate_sha256': binding['candidate_sha256'], 'environment_url': environment_url,
            'operation_intent': operation, 'initiation_request_id': ids['initiation'],
            'content_id': binding['content_id'], 'interface_request_id': ids['interface'],
            'upload_request_id': ids['product'], 'initiated_at': binding['initiated_at'],
            'initiation_evidence_reference': binding['initiation_evidence_reference'],
            'scope_evidence_reference': observation['evidence_reference']}
