#!/usr/bin/env python3
"""Approved Product Groups create only; HTTP/authentication remain core-owned."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlencode
import uuid

ROOT = Path(__file__).resolve().parents[5]
GUIDANCE = Path('pillars/cx/service/service-catalog/manage-product-groups.md')
CONTRACT = GUIDANCE.parent / 'ora-resource/ora_rest_documentation.md'
COLLECTION = '/crmRestApi/resources/11.13.18.05/setupSalesCatalogs'
TASK = 'QSC_MANAGE_PRODUCT_GROUPS'
NAME = 'Manage Product Groups'
OPERATION = 'create-product-group'
TTL = 900
for relative in ['core/runbook/scripts', 'core/data-loader/task-validator/scripts']:
    sys.path.insert(0, str(ROOT / relative))
from runbook_guard import runbook_from_task_context, require_runbook_binding  # noqa: E402
from task_context import resolve_task_context  # noqa: E402


def reject(message):
    raise ValueError(message)


class ProductGroupClientError(ValueError):
    """Task adapter failure carrying only allow-listed, persisted diagnostics."""

    def __init__(self, diagnostic, artifact):
        super().__init__(diagnostic['summary'])
        self.diagnostic = diagnostic
        self.artifact = str(artifact)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            reject('Duplicate JSON keys are not allowed.')
        result[key] = value
    return result


def read(stream):
    return json.load(stream, object_pairs_hook=pairs,
                     parse_constant=lambda _: reject('Nonfinite JSON is not allowed.'))


def document(path):
    with Path(path).open(encoding='utf-8') as stream:
        return read(stream)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc)


def fresh(value):
    try:
        age = (now() - datetime.fromisoformat(value.replace('Z', '+00:00'))).total_seconds()
    except (ValueError, TypeError, AttributeError):
        reject('Invalid Product Groups evidence timestamp.')
    if not 0 <= age <= TTL:
        reject('Product Groups evidence expired; obtain a fresh review and preview.')


def positive_id(value):
    if type(value) is int and 0 < value <= 9223372036854775807:
        return value
    if isinstance(value, str) and re.fullmatch(r'[0-9]{1,19}', value):
        parsed = int(value)
        if 0 < parsed <= 9223372036854775807:
            return parsed
    reject('Invalid Product Groups identity; reconcile without repeating POST.')


def limit(value):
    if isinstance(value, str) and re.fullmatch(r'[0-9]{1,9}', value):
        value = int(value)
    if type(value) is not int or value <= 0:
        reject('Invalid Product Groups Describe length.')
    return value


def local(path, parent):
    raw = Path(path)
    if '..' in raw.parts or any(p.is_symlink() for p in [raw, *raw.parents]):
        reject('Unsafe Product Groups artifact path.')
    resolved = raw.resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to(parent.resolve(strict=True)):
        reject('Product Groups artifact is outside its selected owner.')
    return resolved


def source_contract():
    path = local(ROOT / CONTRACT, ROOT / GUIDANCE.parent)
    contracts = [json.loads(block, object_pairs_hook=pairs) for block in
                 re.findall(r'```json\s*\n(.*?)\n```', path.read_text(), re.S)]
    matches = [c for c in contracts if c.get('taskCode') == TASK and c.get('taskName') == NAME]
    if len(matches) != 1:
        reject('Product Groups contract must resolve exactly once.')
    ops = [op for op in matches[0].get('operations', []) if op.get('id') == OPERATION]
    if len(ops) != 1:
        reject('Product Groups create operation is missing or ambiguous.')
    op = ops[0]
    expected = {'identityField': 'ProdGroupId', 'identityType': 'positive_integer',
                'matchFields': ['InternalName', 'ProdGroupName']}
    if (op.get('enabled') is not True or op.get('method') != 'POST'
            or op.get('path') != COLLECTION or op.get('describePath') != COLLECTION + '/describe'
            or op.get('duplicateFields') != expected['matchFields']
            or op.get('verification') != expected):
        reject('Product Groups create contract is disabled or unsupported.')
    expected_fields = {'InternalName': 150, 'ProdGroupName': 250, 'ActiveFlag': 1,
                       'AllowDuplicateContentFlag': 1, 'UsageRootFlag': 1}
    fields = op.get('fields')
    if not isinstance(fields, dict) or set(fields) != set(expected_fields):
        reject('Unsupported Product Groups fields.')
    for name, size in expected_fields.items():
        spec = fields[name]
        if (spec.get('type') != 'string' or type(spec.get('maxLength')) is not int
                or spec['maxLength'] != size
                or (name in expected['matchFields'] and spec.get('required') is not True)
                or (name not in expected['matchFields'] and spec.get('enum') != ['Y', 'N'])):
            reject('Unsupported Product Groups field contract.')
    return op, hashlib.sha256(path.read_bytes()).hexdigest()


def selection(value):
    ctx = Path(value['taskContextPath'])
    binding = runbook_from_task_context(ctx)
    context = resolve_task_context(ctx, value['taskName'], value['sequence'])
    if (context['task_code'] != TASK or context['task_name'] != NAME
            or context['skill_path'] != GUIDANCE.as_posix()
            or context.get('offering') != 'Service'
            or context.get('functional_area') != 'Service Catalog'
            or value.get('operation') != OPERATION):
        reject('Select the exact Service Product Groups task and create operation.')
    if not re.fullmatch(r'https://[A-Za-z0-9.-]+(?::[0-9]+)?', binding['serverUrl']):
        reject('Product Groups requires a bound HTTPS Fusion origin.')
    project = Path(binding['projectRoot'])
    ctx = local(ctx, project)
    return binding, context, hashlib.sha256(ctx.read_bytes()).hexdigest()


def privilege(path, binding):
    path = local(path, Path(binding['projectRoot']))
    proof = document(path)
    if (proof.get('status') != 'passed' or proof.get('skillId') != 'core.diagnostics.role-access-check'
            or proof.get('environment') != binding['serverUrl'] or proof.get('taskCode') != TASK
            or proof.get('operation') != OPERATION or proof.get('canCreate') is not True
            or proof.get('canRead') is not True):
        reject('Reviewed Product Groups read/create privilege evidence is required.')
    fresh(proof.get('checkedAt'))
    return str(path), digest(proof)


def product_group_output(binding, path):
    """Only new evidence inside this task's fixed namespace is writable."""
    require_runbook_binding(binding)
    path = Path(path)
    if (not path.is_absolute() or '..' in path.parts
            or any(p.is_symlink() for p in [path, *path.parents])):
        reject('Unsafe Product Groups evidence destination.')
    project = Path(binding['projectRoot'])
    if document(project / 'state/project-state.json').get('status') != 'initialized':
        reject('Product Groups requires an initialized project.')
    destination = path.resolve()
    if not destination.is_relative_to(directory(binding)) or destination == directory(binding):
        reject('Evidence must stay in the selected Product Groups namespace.')
    if destination.exists():
        reject('Product Groups evidence output already exists.')
    return destination


def save(binding, path, data):
    path = product_group_output(binding, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    product_group_output(binding, path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return path


def directory(binding):
    return Path(binding['projectRoot']) / 'artifacts/pillars/cx/service/service-catalog/product-group-rest'


def client_failure(binding, target, method, *, stdout='', stderr='',
                   returncode=None, timed_out=False):
    # Adapt this task's core CLI result; never persist raw stderr, URLs, headers,
    # exception text or server bodies, which can include credentials/setup data.
    def bounded(value):
        if isinstance(value, bytes):
            value = value.decode('utf-8', errors='replace')
        return value[:65536] if isinstance(value, str) else ''

    output = '\n'.join([bounded(stdout), bounded(stderr)])
    structured = {}
    for line in [bounded(stderr), bounded(stdout), *output.splitlines()]:
        try:
            candidate = json.loads(re.sub(r'^Error:\s*', '', line.strip()))
        except (ValueError, TypeError):
            continue
        if isinstance(candidate, dict):
            structured = candidate
            if isinstance(candidate.get('error'), dict):
                structured = {**candidate, **candidate['error']}
            break
    statuses = set(re.findall(r'\bHTTP(?:\s+status)?\s*[:=]?\s*([1-5][0-9]{2})\b', output, re.I))
    for key in ['http_status', 'httpStatus', 'status']:
        value = structured.get(key)
        if type(value) is int or isinstance(value, str):
            if re.fullmatch(r'[1-5][0-9]{2}', str(value)):
                statuses.add(str(value))
    status = int(next(iter(statuses))) if len(statuses) == 1 else None
    allowed = {'input_validation', 'catalog_or_metadata_mismatch', 'auth_authz',
               'transport_environment', 'fusion_api_error', 'process_timeout',
               'process_failed', 'artifact_persistence', 'approval_blocker'}
    failure_class = structured.get('failure_class', structured.get('failureClass'))
    if not isinstance(failure_class, str) or failure_class not in allowed:
        failure_class = 'fusion_api_error' if status and status >= 400 else 'transport_environment'
    if status in {401, 403}:
        failure_class = 'auth_authz'
    if timed_out:
        failure_class = 'process_timeout'

    def identifier(keys, pattern):
        candidates = [structured.get(key) for key in keys]
        candidates += re.findall(pattern, output, re.I)
        values = {v for v in candidates if isinstance(v, str)
                  and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}', v)}
        return next(iter(values)) if len(values) == 1 else None

    request_id = identifier(['request_id', 'requestId', 'requestID'],
                            r'\b(?:request[_-]?id|x-request-id)[\s"\x27]*[:=][\s"\x27]*([A-Za-z0-9][A-Za-z0-9_.:-]{0,159})(?![A-Za-z0-9_.:-])')
    ecid = identifier(['ecid', 'ECID'],
                      r'\b(?:ecid|x-oracle-dms-ecid)[\s"\x27]*[:=][\s"\x27]*([A-Za-z0-9][A-Za-z0-9_.:-]{0,159})(?![A-Za-z0-9_.:-])')
    diagnostic = {'failure_class': failure_class,
                  'createdAt': now().isoformat(), 'operation': OPERATION,
                  'environment': binding['serverUrl'],
                  'summary': 'Shared REST client ' + ('timed out' if timed_out else 'failed')
                             + (f' (HTTP {status})' if status else '')
                             + '; reconcile retained task evidence; never retry a write.',
                  'method': method, 'http_status': status, 'request_id': request_id,
                  'ecid': ecid, 'client_returncode': returncode,
                  'timeout_seconds': 90 if timed_out else None,
                  'diagnostics_policy': 'Allow-listed metadata only; raw client output suppressed.',
                  'artifact_refs': []}
    if target.is_file():
        diagnostic['artifact_refs'].append(str(target))
    request = target.with_name(target.stem + '-request.json')
    if request.is_file():
        diagnostic['artifact_refs'].append(str(request))
    artifact = save(binding, target.with_name(target.stem + '-diagnostic.json'), diagnostic)
    raise ProductGroupClientError(diagnostic, artifact) from None


def transport(binding, path, method='GET', body=None):
    # No HTTP, token handling, refresh or retry implementation is owned by this pillar.
    target = directory(binding) / 'transport' / (uuid.uuid4().hex + '.json')
    product_group_output(binding, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    product_group_output(binding, target)
    command = [sys.executable, str(ROOT / 'core/fusion-api/rest-api-client/scripts/fusion_rest_client.py'),
               binding['serverUrl'] + path, '--method', method, '--header',
               'REST-Framework-Version=9', '--output', str(target), '--timeout', '60']
    if body is not None:
        source = save(binding, target.with_name(target.stem + '-request.json'), body)
        command += ['--body-file', str(source)]
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired as error:
        client_failure(binding, target, method, stdout=error.stdout,
                       stderr=error.stderr, timed_out=True)
    except OSError:
        client_failure(binding, target, method)
    statuses = re.findall(r'(?m)^HTTP (\d{3})$', result.stdout)
    if result.returncode or len(statuses) != 1 or not 200 <= int(statuses[0]) < 300:
        client_failure(binding, target, method, stdout=result.stdout,
                       stderr=getattr(result, 'stderr', ''), returncode=result.returncode)
    return document(target)


def check_describe(data, op):
    if not isinstance(data, dict):
        reject('Product Groups Describe must be an object.')
    resources = data.get('Resources')
    if not isinstance(resources, dict):
        reject('Product Groups Describe resources are missing.')
    resource = resources.get('setupSalesCatalogs', {})
    if not isinstance(resource, dict) or not isinstance(resource.get('collection'), dict):
        reject('Product Groups collection Describe is missing.')
    actions = resource['collection'].get('actions')
    if not isinstance(actions, list) or not any(
            a.get('name') == 'create' and a.get('method') == 'POST'
            for a in actions if isinstance(a, dict)):
        reject('Describe does not confirm Product Groups collection create.')
    attributes = resource.get('attributes')
    if not isinstance(attributes, list):
        reject('Product Groups Describe attributes are missing.')
    if any(not isinstance(a, dict) or not isinstance(a.get('name'), str) for a in attributes):
        reject('Malformed Product Groups Describe attributes.')
    names = [a.get('name') for a in attributes]
    if len(names) != len(set(names)):
        reject('Ambiguous Product Groups Describe attributes.')
    attrs = {a['name']: a for a in attributes}
    for name, spec in op['fields'].items():
        actual = attrs.get(name, {})
        if (actual.get('type') != 'string' or actual.get('creatable') is False
                or limit(actual.get('maxLength', actual.get('precision'))) < spec['maxLength']
                or (spec.get('required') and actual.get('mandatory') is not True)):
            reject('Describe does not confirm Product Groups field contract.')


def payload(body, op):
    if not isinstance(body, dict) or set(body) - set(op['fields']):
        reject('Unknown Product Groups payload fields.')
    for name, spec in op['fields'].items():
        value = body.get(name)
        if spec.get('required') and (not isinstance(value, str) or not value.strip()):
            reject('Both Product Groups names are required.')
        if name in body and (not isinstance(value, str) or len(value) > spec['maxLength']
                             or ('enum' in spec and value not in spec['enum'])):
            reject('Invalid Product Groups payload value.')


def duplicate_path(body):
    terms = [name + "='" + body[name].replace("'", "''") + "'"
             for name in ['InternalName', 'ProdGroupName']]
    return COLLECTION + '?' + urlencode({'q': ' OR '.join(terms), 'onlyData': 'true',
        'fields': 'ProdGroupId,InternalName,ProdGroupName', 'limit': '2'})


def unique(data):
    if (not isinstance(data, dict) or data.get('items') != [] or data.get('hasMore') is not False
            or data.get('count', 0) != 0):
        reject('Product Groups duplicate check is nonempty or incomplete.')


def validate(value, client=transport):
    binding, context, context_hash = selection(value)
    op, source_hash = source_contract()
    body = value.get('payload')
    payload(body, op)
    proof, proof_hash = privilege(value['privilegeEvidence'], binding)
    describe = client(binding, COLLECTION + '/describe')
    check_describe(describe, op)
    unique(client(binding, duplicate_path(body)))
    preview = {'schemaVersion': '1.0', 'operation': OPERATION, 'createdAt': now().isoformat(),
        'binding': binding, 'task': context, 'contextHash': context_hash,
        'guidanceHash': hashlib.sha256(local(ROOT / GUIDANCE, ROOT / 'pillars').read_bytes()).hexdigest(),
        'contractHash': source_hash, 'privilegeEvidence': proof, 'privilegeHash': proof_hash,
        'selection': {k: value[k] for k in ['taskContextPath', 'taskName', 'sequence', 'operation']},
        'method': 'POST', 'path': COLLECTION, 'payload': body, 'describeHash': digest(describe)}
    path = save(binding, directory(binding) / (uuid.uuid4().hex + '-preview.json'), preview)
    return {'status': 'approval_required', 'previewPath': str(path), 'previewSha256': digest(preview),
            'environment': binding['serverUrl'], 'method': 'POST', 'path': COLLECTION, 'payload': body}


def verify(value):
    if value.get('approved') is not True:
        reject('Exact Product Groups preview approval is required.')
    path = local(value['previewPath'], ROOT / 'project')
    preview = document(path)
    if digest(preview) != value.get('previewSha256'):
        reject('Product Groups preview digest changed.')
    fresh(preview['createdAt'])
    binding, context, context_hash = selection(preview['selection'])
    require_runbook_binding(preview['binding'])
    if (binding != preview['binding'] or context != preview['task']
            or context_hash != preview['contextHash'] or path.parent != directory(binding)):
        reject('Product Groups preview context/binding changed.')
    op, source_hash = source_contract()
    if (source_hash != preview['contractHash'] or preview['operation'] != OPERATION
            or preview['method'] != 'POST' or preview['path'] != COLLECTION
            or hashlib.sha256(local(ROOT / GUIDANCE, ROOT / 'pillars').read_bytes()).hexdigest() != preview['guidanceHash']):
        reject('Product Groups preview source contract changed.')
    payload(preview['payload'], op)
    _, proof_hash = privilege(preview['privilegeEvidence'], binding)
    if proof_hash != preview['privilegeHash']:
        reject('Product Groups privilege evidence changed.')
    return path, preview, op


def execute(value, client=transport):
    path, preview, op = verify(value)
    binding = preview['binding']
    save(binding, path.with_name(path.stem + '-attempt.json'),
         {'status': 'attempted', 'startedAt': now().isoformat(), 'previewSha256': value['previewSha256']})
    stage, identity = 'preflight', None
    try:
        describe = client(binding, COLLECTION + '/describe')
        check_describe(describe, op)
        if digest(describe) != preview['describeHash']:
            reject('Product Groups Describe changed; prepare a fresh preview.')
        unique(client(binding, duplicate_path(preview['payload'])))
        verify(value)  # Recheck expiry, sources and binding immediately before the one POST.
        stage = 'create'
        created = client(binding, COLLECTION, 'POST', preview['payload'])
        if not isinstance(created, dict):
            reject('Invalid Product Groups create response; reconcile without repeating POST.')
        identity = positive_id(created.get('ProdGroupId'))
        if any(created.get(k) != v for k, v in preview['payload'].items()):
            reject('Created Product Groups names differ; reconcile without repeating POST.')
        stage = 'verification'
        actual = client(binding, COLLECTION + '/' + str(identity))
        if (not isinstance(actual, dict) or positive_id(actual.get('ProdGroupId')) != identity
                or any(actual.get(k) != v for k, v in preview['payload'].items())):
            reject('Fresh Product Groups verification failed; reconcile without repeating POST.')
        result = {'status': 'verified', 'environment': binding['serverUrl'], 'recordId': identity,
                  'values': {k: actual[k] for k in ['InternalName', 'ProdGroupName']}, 'verifiedAt': now().isoformat()}
        save(binding, path.with_name(path.stem + '-result.json'), result)
        return result
    except Exception as error:
        failure_class = (error.diagnostic['failure_class'] if isinstance(error, ProductGroupClientError) else
                         'process_timeout' if isinstance(error, (TimeoutError, subprocess.TimeoutExpired)) else
                         'artifact_persistence' if isinstance(error, OSError) else
                         'fusion_api_error' if stage in {'create', 'verification'} else
                         'catalog_or_metadata_mismatch')
        save(binding, path.with_name(path.stem + '-failure.json'),
             {'status': 'blocked_or_uncertain', 'stage': stage, 'environment': binding['serverUrl'],
              'failure_class': failure_class,
              'operation': OPERATION, 'recordId': identity,
              'diagnostic': error.diagnostic if isinstance(error, ProductGroupClientError) else None,
              'artifact_refs': [error.artifact] if isinstance(error, ProductGroupClientError) else [],
              'recommended_action': 'Reconcile retained evidence; never replay this preview or retry POST.'})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ['validate-fscr-task-rest-payload', 'verify-fscr-task-rest-preview', 'fscr-task-rest']:
        sub.add_parser(name).add_argument('--input-stdin', action='store_true', required=True)
    args = parser.parse_args(argv)
    try:
        value = read(sys.stdin)
        if not isinstance(value, dict):
            reject('Product Groups command input must be an object.')
        if args.command == 'validate-fscr-task-rest-payload':
            result = validate(value)
        elif args.command == 'verify-fscr-task-rest-preview':
            path, preview, _ = verify(value)
            result = {'status': 'verified', 'previewPath': str(path),
                      'previewSha256': value['previewSha256'], 'payload': preview['payload']}
        else:
            result = execute(value)
        print(json.dumps(result))
        return 0
    except (ValueError, OSError, KeyError, TypeError):
        print('Product Groups operation blocked or uncertain; inspect retained project evidence. Never retry a write.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
