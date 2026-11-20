"""Customer-required Run Book attribution capability from public REST metadata.

Pure evidence interpretation: no core internals, credentials, approval or writes.
"""
from urllib.parse import urlsplit
import customers_package as package
from customer_registration_review import timestamp

PATH = '/hcmRestApi/resources/latest/dataLoaderDataSets/describe'


def review(environment, evidence):
    require = package.require
    url = urlsplit(environment)
    require(url.scheme == 'https' and url.hostname and not url.username
            and not url.password and url.path in ('', '/') and not url.query
            and not url.fragment, 'CAPABILITY_ENVIRONMENT')
    require(isinstance(evidence, dict) and set(evidence) == {
        'schema_version', 'environment_url', 'path', 'captured_at',
        'evidence_reference', 'response'}, 'CAPABILITY_EVIDENCE_SCHEMA')
    require(evidence['schema_version'] == 'ar-customer-loader-capability-v1'
            and evidence['environment_url'] == environment and evidence['path'] == PATH,
            'CAPABILITY_EVIDENCE_BINDING')
    timestamp(evidence['captured_at'])
    require(isinstance(evidence['evidence_reference'], str)
            and evidence['evidence_reference'].strip(), 'CAPABILITY_PROVENANCE')
    raw = evidence['response']
    require(isinstance(raw, dict), 'CAPABILITY_RESPONSE_SCHEMA')
    # Restrict the result to the selected resource, rather than accepting a
    # similarly named parameter in another resource or action.
    resources = raw.get('Resources', raw.get('resources'))
    require(isinstance(resources, dict) and isinstance(resources.get('dataLoaderDataSets'), dict),
            'CAPABILITY_RESOURCE_MISSING')
    resource = resources['dataLoaderDataSets']
    selected = []
    # ADF describe publishes collection actions beneath `collection`.
    # Also accept the direct resource form; never scan child resources or
    # item actions for a similarly named capability.
    for holder in (resource, resource.get('collection', {})):
        require(isinstance(holder, dict), 'CAPABILITY_RESPONSE_SCHEMA')
        actions = holder.get('actions', holder.get('Actions'))
        if isinstance(actions, dict) and 'initiateDataLoad' in actions:
            selected.append(actions['initiateDataLoad'])
        elif isinstance(actions, list):
            selected.extend(a for a in actions if isinstance(a, dict) and a.get('name') == 'initiateDataLoad')
    require(len(selected) == 1 and isinstance(selected[0], dict), 'CAPABILITY_ACTION_MISSING_OR_AMBIGUOUS')

    parameters = selected[0].get('parameters')
    require(isinstance(parameters, list) and len([p for p in parameters
        if isinstance(p, dict) and p.get('name') == 'runBookTaskCode']) == 1,
        'CAPABILITY_RUNBOOK_TASK_CODE_UNAVAILABLE')
    return {'schema_version': 'ar-customer-loader-capability-review-v1',
            'status': 'RUNBOOK_TASK_CODE_ADVERTISED',
            'evidence_sha256': package.fingerprint(evidence),
            'environment_url': environment, 'captured_at': evidence['captured_at'],
            'execution_authorized': False, 'server_association_verified': False}
