"""Plan BOSS reads and transform delegated Core results into a complete risk tree.

Like Activate Algorithms' execute.py, this module performs no HTTP, OAuth,
token-cache, Core-client invocation, or automatic retry work.
"""
import argparse
from contextlib import contextmanager, nullcontext
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import quote

from fscr_context import REPOSITORY, bind_request
from generate_rules import ALGORITHMS, build_catalog
from evaluate_roles import validate_request
from workspace_paths import require_complete_normalization, validate_project_artifact

CODES = list(ALGORITHMS)
BASE = '/api/boss/data/objects/ora/riskMgmtRisk/accessControls/v1/'
MAX_PAGES = 1000


class ExtractionError(ValueError):
    def __init__(self, message, failure_class='catalog_or_metadata_mismatch', details=None):
        super().__init__(message)
        self.failure_class = failure_class
        self.details = details or {}


def field(record, name, context, identifier=False):
    value = record.get(name) if isinstance(record, dict) else None
    if identifier and isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if not isinstance(value, str) or not value.strip():
        raise ExtractionError(f'{context}: missing or invalid {name}')
    return value


def project_path(path, request_id=None):
    return validate_project_artifact(path, request_id, repository=REPOSITORY)


def load_responses(specifications, run_directory):
    responses = {}
    for specification in specifications:
        request_id, separator, filename = specification.partition('=')
        if not separator or not request_id or not filename or request_id in responses:
            raise ValueError('--core-response must be a unique request-id=Core-result.json')
        path = Path(filename).resolve()
        if not path.is_relative_to(Path(run_directory).resolve()):
            raise ValueError('Core evidence must belong to this request directory')
        result = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(result, dict):
            raise ValueError('Core evidence must be a JSON object')
        responses[request_id] = result
    return responses


class CoreResults:
    def __init__(self, request, run_key, responses):
        self.request = request
        self.run_key = run_key
        self.responses = responses
        self.pending = {}
        self.used = set()

    def get(self, resource, query):
        operation = {'service': 'boss', 'method': 'GET', 'endpoint': BASE + resource,
                     'query': query}
        context = {'assessment_request_id': self.request['requestId'],
                   'environment': self.request['environment'], 'run_key': self.run_key}
        digest = hashlib.sha256(json.dumps(dict(operation, **context), sort_keys=True,
                                           separators=(',', ':')).encode()).hexdigest()[:24]
        request_id = 'boss-' + digest
        manifest = dict(operation, id=request_id, **context,
                        core_skill_id='core.fusion-api.rest-api-client',
                        core_client_request={'method': 'GET', 'endpoint': operation['endpoint'],
                                             'query': query, 'service': 'boss'})
        if request_id not in self.responses:
            self.pending[request_id] = manifest
            return None
        self.used.add(request_id)
        result = self.responses[request_id]
        if (result.get('request_id') != request_id
                or result.get('environment') != context['environment']):
            raise ExtractionError('Core evidence request/environment mismatch')
        status = result.get('status')
        if isinstance(status, bool) or not isinstance(status, int):
            raise ExtractionError('Core evidence requires an integer HTTP status')
        if not 200 <= status < 300:
            category = ('auth_expired_or_invalid' if status == 401 else
                        'authorization_or_privilege' if status == 403 else 'fusion_api_error')
            raise ExtractionError(f'Core request {request_id} returned HTTP {status}', category)
        body = result.get('body')
        if (not isinstance(body, dict) or not isinstance(body.get('items'), list)
                or not all(isinstance(item, dict) for item in body['items'])
                or not isinstance(body.get('hasMore'), bool)):
            raise ExtractionError('Core collection requires object items and boolean hasMore')
        return body

    def one(self, resource, query, context=None):
        body = self.get(resource, query)
        if body is None:
            return None
        if len(body['items']) != 1 or body['hasMore']:
            details = {'resource': resource, 'lookup': query.get('$filter'),
                       'result_count': len(body['items']), 'has_more': body['hasMore'],
                       'context': context}
            raise ExtractionError(
                f'{context or resource}: expected exactly one unpaginated matching record; '
                f'lookup={query.get("$filter")!r}, returned={len(body["items"])}, '
                f'hasMore={body["hasMore"]}', details=details)
        return body['items'][0]

    def pages(self, resource, query):
        rows, offset, seen_pages = [], 0, set()
        for _ in range(MAX_PAGES):
            body = self.get(resource, dict(query, **{'$limit': '100', '$offset': str(offset)}))
            if body is None:
                return None
            fingerprint = json.dumps(body['items'], sort_keys=True)
            if body['hasMore'] and (not body['items'] or fingerprint in seen_pages):
                raise ExtractionError('Empty or repeated page while hasMore=true')
            seen_pages.add(fingerprint)
            rows.extend(body['items'])
            if not body['hasMore']:
                return rows
            offset += len(body['items'])
        raise ExtractionError('Pagination exceeded the bounded page limit', 'process_timeout')


def plan_extraction(request, run_key, responses):
    request, _, _ = validate_request(request)
    client = CoreResults(request, run_key, responses)
    tree = []
    for code in CODES:
        algorithm = client.one('providedAccessAlgorithms/$views/detailed',
                               {'$filter': f"referenceCode='{code}'", '$fields': 'id,name'},
                               context=f'algorithm {code}')
        if algorithm is None:
            continue
        algorithm_id = field(algorithm, 'id', code, True)
        entry = {'referenceCode': code, 'id': algorithm_id,
                 'name': field(algorithm, 'name', code), 'entitlements': []}
        refs = client.pages(f'providedAccessAlgorithms/{quote(algorithm_id, safe="")}/algorithmReferences',
                            {'$filter': "referenceType='ENTITLEMENTS'", '$fields': 'referenceId'})
        if refs is None:
            continue
        if len(refs) != ALGORITHMS[code]:
            raise ExtractionError(f'{code}: incorrect entitlement dimension count')
        entitlement_ids = [field(ref, 'referenceId', code, True) for ref in refs]
        if len(set(entitlement_ids)) != len(entitlement_ids):
            raise ExtractionError(f'{code}: duplicate entitlement reference')
        complete = True
        for entitlement_id in entitlement_ids:
            escaped = entitlement_id.replace("'", "''")
            entitlement = client.one('providedEntitlements/$views/detailed',
                                     {'$filter': f"id='{escaped}'", '$fields': 'name'},
                                     context=f'algorithm {code}; entitlement {entitlement_id}')
            points = client.pages(f'providedEntitlements/{quote(entitlement_id, safe="")}/accesses',
                                  {'$fields': 'primaryAccessPoint.code,primaryAccessPoint.name'})
            if entitlement is None or points is None:
                complete = False
                continue
            accesses = []
            for item in points:
                point = item.get('primaryAccessPoint')
                accesses.append({'code': field(point, 'code', code),
                                 'name': field(point, 'name', code)})
            entry['entitlements'].append({'id': entitlement_id,
                                           'name': field(entitlement, 'name', code),
                                           'accessPoints': accesses})
        if complete:
            tree.append(entry)
    unknown = set(responses) - client.used
    if unknown:
        raise ExtractionError('Unexpected or unreachable Core evidence; use only this run\'s emitted requests')
    plan = {'status': 'awaiting_core_responses' if client.pending else 'completed',
            'assessment_request_id': request['requestId'], 'environment': request['environment'],
            'run_key': run_key, 'core_skill_id': 'core.fusion-api.rest-api-client',
            'requests': list(client.pending.values()), 'completed_response_ids': sorted(client.used)}
    if client.pending:
        return None, plan
    # Reuse the evaluator's strict six-algorithm/dimension/duplicate validation.
    build_catalog(json.dumps(tree).encode('utf-8'), request['environment'])
    return tree, plan


@contextmanager
def assessment_lock(output, dry_run=False):
    """Serialize same-directory handoffs and publication; never remove another run's lock."""
    if dry_run:
        yield
        return
    directory = Path(output).parent
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / '.risk-and-security-checkup.lock'
    try:
        stream = lock.open('x', encoding='utf-8')
    except FileExistsError:
        raise ValueError('Assessment directory is locked; check for a running process before recovery') from None
    try:
        with stream:
            stream.write(str(os.getpid()))
            stream.flush()
            yield
    finally:
        lock.unlink()


def stage_document(path, content):
    """Create this assessment document in a unique exclusive same-directory file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', prefix='.rsc-', suffix='.tmp',
                                         dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        return temporary
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def publish_document(temporary, destination, exclusive=True):
    if exclusive:
        # Atomic no-replace publication, including destinations created after preflight.
        os.link(temporary, destination)
    else:
        # Only the validated same-run request plan may be refreshed under the run lock.
        Path(temporary).replace(destination)


def write_json(path, document, exclusive=False):
    raw = json.dumps(document, ensure_ascii=False, indent=2) + '\n'
    temporary = stage_document(path, raw.encode('utf-8'))
    try:
        publish_document(temporary, path, exclusive)
    finally:
        temporary.unlink(missing_ok=True)


def prepare(request, output, specifications, plan_output=None, dry_run=False, *, _lock_held=False):
    output = project_path(output)
    with nullcontext() if _lock_held else assessment_lock(output, dry_run):
        return _prepare(request, output, specifications, plan_output, dry_run)


def _prepare(request, output, specifications, plan_output=None, dry_run=False):
    output = project_path(output)
    plan_output = project_path(plan_output or output.parent / 'core-requests.json')
    if plan_output == output or not plan_output.is_relative_to(output.parent):
        raise ValueError('Request plan must be a separate artifact in this run directory')
    if output.exists():
        raise ValueError('Output already exists; preserve it and select a new request directory')
    responses = load_responses(specifications, output.parent)
    for spec in specifications:
        if Path(spec.partition('=')[2]).resolve() in {output, plan_output}:
            raise ValueError('Output artifacts cannot overwrite Core evidence')
    run_key = output.parent.relative_to(REPOSITORY).as_posix()
    replace_plan = plan_output.exists()
    if replace_plan:
        previous = json.loads(plan_output.read_text(encoding='utf-8'))
        if (not isinstance(previous, dict) or previous.get('run_key') != run_key
                or previous.get('assessment_request_id') != request['requestId']
                or previous.get('environment') != request['environment']):
            raise ValueError('Existing request plan belongs to a different run; refusing overwrite')
    try:
        tree, plan = plan_extraction(request, run_key, responses)
    except (ValueError, OSError) as error:
        if not dry_run:
            write_json(plan_output, {'status': 'failed', 'stage': 'runtime_metadata',
                       'failure_class': getattr(error, 'failure_class', 'input_validation'),
                       'details': getattr(error, 'details', {}),
                       'message': str(error), 'environment': request['environment'],
                       'run_key': run_key,
                       'assessment_request_id': request['requestId'], 'requests': [],
                       'recommended_action': 'Correct Core evidence or resolve the delegated Core error; do not fall back to prior metadata.'},
                       exclusive=not replace_plan)
        raise
    if not dry_run:
        write_json(plan_output, plan, exclusive=not replace_plan)
    return tree, plan


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Prepared role request in the selected project')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--properties', type=Path)
    parser.add_argument('--core-response', action='append', default=[], help='request-id=Core-result.json; repeat for every returned result')
    parser.add_argument('--request-plan-output', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='Validate and print the next read plan without writing artifacts')
    args = parser.parse_args(argv)
    request = bind_request(json.loads(args.input.read_text(encoding='utf-8')), args.properties)
    project_path(args.input, request['requestId'])
    project_path(args.output, request['requestId'])
    require_complete_normalization(args.input, request['requestId'])
    if args.request_plan_output:
        project_path(args.request_plan_output, request['requestId'])
    if args.input.resolve() in {args.output.resolve(), (args.request_plan_output or args.output.parent / 'core-requests.json').resolve()}:
        raise ValueError('Extraction artifacts cannot overwrite role input')
    with assessment_lock(project_path(args.output), args.dry_run):
        tree, plan = prepare(request, args.output, args.core_response, args.request_plan_output,
                             args.dry_run, _lock_held=True)
        if tree is not None and not args.dry_run:
            write_json(args.output, tree, exclusive=True)
    print(json.dumps(plan if args.dry_run else {'status': plan['status'], 'pending_requests': len(plan['requests'])}))
    return 0 if tree is not None or args.dry_run else 2


if __name__ == '__main__':
    raise SystemExit(main())
