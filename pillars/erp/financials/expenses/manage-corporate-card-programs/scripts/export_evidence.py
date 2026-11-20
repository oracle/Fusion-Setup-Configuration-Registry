"""Task-owned FSM export evidence adapter; core/shared own auth and transport.

Pattern: Payments Manage Transmission Configurations sanitize_export.py.
Raw exports remain in memory; only sanitized, exact-shape snapshots are saved.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import time
import uuid
from urllib.error import URLError
import zipfile
import xml.etree.ElementTree as ET

from prepare_fsm_package import TASK, META, inspect_package
ISSUERS = 'EXM_MANAGE_CORPORATE_CARD_ISSUERS'
MAPPINGS = 'EXM_MANAGE_CORPORATE_CARD_EXPENSE_TYPE_MAPPING_RULES'
WITHHELD = '[WITHHELD]'
SENSITIVE = {'username', 'encryptedpassword', 'password', 'secret', 'clientsecret',
             'accesstoken', 'refreshtoken', 'privatekey'}


def sanitize(content, task, environment):
    """Return same-header evidence, never an import archive or credential proof."""
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        entries = z.infolist()
        names = [e.filename for e in entries]
        if len(names) != len(set(names)) or META not in names:
            raise ValueError('Invalid export inventory')
        if any('/' in n or '\\' in n or not (n.endswith('.csv') or n == META) for n in names):
            raise ValueError('Invalid export member')
        if len(entries) > 30 or sum(e.file_size for e in entries) > 60_000_000 or any(e.flag_bits & 1 for e in entries):
            raise ValueError('Export exceeds limits or is encrypted')
        members = {n: z.read(n) for n in names}
    raw = members[META]
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('Unsafe metadata')
    xml = ET.fromstring(raw)
    def value(tag):
        found = xml.findall('./MigrationProcessCSVMetadataVORow/'+tag)
        if len(found) != 1 or not found[0].text:
            raise ValueError('Missing export identity')
        return found[0].text
    if value('ObjectShortName') != task or value('ObjectType') != 'TASK' or value('ProcessEnv') != environment or value('ProcessStatus') != 'COMPLETED':
        raise ValueError('Export identity or status mismatch')
    omitted = set(); tables = {}; count = 0
    for name in names:
        if name == META: continue
        rows = list(csv.reader(io.StringIO(members[name].decode('utf-8-sig'), newline=''), strict=True))
        if not rows or len(set(rows[0])) != len(rows[0]) or any(not h for h in rows[0]) or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError('Malformed export table')
        for index, header in enumerate(rows[0]):
            key = re.sub('[^a-z0-9]', '', header.lower())
            if key in SENSITIVE or any(s in key for s in ('password','token','secret','privatekey')):
                # EnableCcTokenFlag is a public enum, not a token value.
                if header == 'EnableCcTokenFlag': continue
                for row in rows[1:]:
                    if row[index]: omitted.add(row[index]); row[index] = WITHHELD; count += 1
        tables[name] = rows
    if any(v.encode() in raw for v in omitted):
        raise ValueError('Sensitive data in metadata')
    # Suppress repeated credential text in other CSV values as well.
    for name, rows in tables.items():
        for row in rows[1:]:
            for i, val in enumerate(row):
                if val != WITHHELD:
                    for secret in sorted(omitted, key=len, reverse=True):
                        val = val.replace(secret, WITHHELD)
                    row[i] = val
        stream = io.StringIO(newline=''); csv.writer(stream, lineterminator='\r\n').writerows(rows)
        members[name] = stream.getvalue().encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(members): z.writestr(name, members[name])
    safe = out.getvalue()
    if task == TASK: inspect_package(io.BytesIO(safe), environment)
    return safe, {'status': 'SANITIZED', 'taskCode': task, 'processEnvironment': environment,
                  'release': value('ProcessRelease'), 'withheldCellCount': count,
                  'credentialPreservation': 'NOT_VERIFIED', 'importable': False,
                  'sha256': hashlib.sha256(safe).hexdigest()}


def process_id(response, scope):
    if not isinstance(response, dict) or response.get('TaskCode', scope.primary_code) != scope.primary_code:
        raise ValueError('Export task mismatch')
    children = response.get(scope.process_child)
    if isinstance(children, dict):
        if children.get('hasMore') not in (None, False): raise ValueError('Incomplete export response')
        children = children.get('items')
    if not isinstance(children, list) or len(children) != 1 or not isinstance(children[0], dict):
        raise ValueError('Ambiguous export process')
    child = children[0]; pid = child.get('ProcessId')
    if child.get('TaskCode', scope.primary_code) != scope.primary_code or isinstance(pid, bool) or not re.fullmatch('[1-9][0-9]*', str(pid)):
        raise ValueError('Invalid export process identity')
    return str(pid)


def create_process(props, token, scope, receipt, binding, create_export, progress=None):
    """Keep a private receipt descriptor pinned across the one-attempt POST."""
    pending = dict(binding, status='SUBMISSION_UNCONFIRMED',
                   startedAt=datetime.now(timezone.utc).isoformat())
    if progress is not None: progress['stage'] = 'receipt_write'
    if '..' in Path(receipt).parts:
        raise ValueError('Traversal is not allowed')
    receipt = Path(os.path.abspath(receipt))
    directory = open_receipt_parent(receipt.parent)
    try:
        descriptor = os.open(receipt.name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
        with os.fdopen(descriptor, 'w+', encoding='utf-8') as stream:
            def verify():
                current = open_receipt_parent(receipt.parent)
                try:
                    original, reopened = os.fstat(directory), os.fstat(current)
                    entry = os.stat(receipt.name, dir_fd=directory, follow_symlinks=False)
                    opened = os.fstat(stream.fileno())
                    if ((original.st_dev, original.st_ino) != (reopened.st_dev, reopened.st_ino)
                            or (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino)
                            or opened.st_nlink != 1):
                        raise OSError('Export receipt or parent changed')
                finally:
                    os.close(current)

            verify()
            json.dump(pending, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
            if progress is not None: progress['stage'] = 'export_create'
            response = create_export(props, token, scope.primary_code,
                                     template_only=scope.template_only)
            pending.update(status='CREATED', processId=process_id(response, scope))
            if progress is not None: progress.update(stage='receipt_update', processId=pending['processId'])
            verify()
            stream.seek(0)
            stream.truncate()
            json.dump(pending, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
            verify()
    finally:
        os.close(directory)
    return pending


def open_receipt_parent(parent):
    """Open the receipt's lexical ancestry without following any symlink."""
    if (not hasattr(os, 'O_NOFOLLOW') or not hasattr(os, 'O_DIRECTORY')
            or os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd):
        raise OSError('Safe export receipt persistence is unavailable')
    parent = Path(parent)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(parent.anchor, flags)
    try:
        for part in parent.parts[1:]:
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        return directory
    except BaseException:
        os.close(directory)
        raise


def services():
    repo = Path(__file__).resolve().parents[6]
    sys.path.insert(0, str(repo/'shared/setup-export/task-level-export/scripts'))
    import get_setup_task_csv_export_result as shared
    import create_setup_task_csv_export as create
    import fsm_csv_export_engine as engine
    return shared, create, engine


def safe_path(path):
    if '..' in Path(path).parts:
        raise ValueError('Traversal is not allowed')
    path = Path(os.path.abspath(path))
    for item in (*reversed(path.parents), path):
        if item.is_symlink():
            raise ValueError('Symlinked export paths are not allowed')
        if item.exists() and item != path and not item.is_dir():
            raise ValueError('Invalid path ancestor')
    return path


def initialized_project(path, repo):
    project = safe_path(path)
    if project.parent != safe_path(repo)/'project' or project.name.startswith('_'):
        raise ValueError('Use an initialized repository project')
    state_path = safe_path(project/'state/project-state.json')
    if not state_path.is_file() or state_path.stat().st_size > 1024*1024:
        raise ValueError('Initialized project state required')
    state = json.loads(state_path.read_text())
    if (not isinstance(state, dict) or state.get('project_id') != project.name
            or state.get('status') not in {'initialized','in_progress','blocked','ready_for_review'}):
        raise ValueError('Initialized project identity required')
    return project


def within(path, root):
    path, root = safe_path(path), safe_path(root)
    if path == root or root not in path.parents:
        raise ValueError('Artifact must be inside project exports')
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_path(path)
    return path


def validate_result_identity(process, items, pid, task):
    if not isinstance(process, dict):
        raise ValueError('Invalid process response')
    if not isinstance(items, list) or len(items) > 1:
        raise ValueError('Ambiguous export result')
    for row in [process, *items]:
        if (not isinstance(row, dict) or str(row.get('ProcessId', pid)) != pid
                or row.get('TaskCode') not in (None, task)):
            raise ValueError('Export result identity mismatch')


class ProfileChangedError(ValueError):
    pass


def profile_guard(properties_path, props):
    """Freeze the selected configuration, as in the Expenses SIC collector."""
    fingerprint = hashlib.sha256(properties_path.read_bytes()).digest()
    selected = dict(props)

    def unchanged():
        if (props != selected or
                hashlib.sha256(properties_path.read_bytes()).digest() != fingerprint):
            raise ProfileChangedError('Selected authentication profile changed')
    return unchanged


def acquire_token(shared, props, args, unchanged, *, refresh=False):
    unchanged()
    token = shared.get_access_token(
        props, open_browser=args.open_browser, token_cache='auto',
        # This task never consumes a token from a previous login/session.
        # Keep core responsible for login, storage and the returned bound token.
        force_login=True,
        callback_timeout=shared.DEFAULT_CALLBACK_TIMEOUT_SECONDS)
    unchanged()
    return token


def failure_class(exc, stage):
    if isinstance(exc, ProfileChangedError):
        return 'authorization_or_privilege'
    code = getattr(exc, 'status_code', None)
    if code in (401, 403):
        return 'auth_expired_or_invalid' if code == 401 else 'authorization_or_privilege'
    if isinstance(code, int):
        return 'fusion_api_error'
    if isinstance(exc, (TimeoutError, ConnectionError, URLError)) or isinstance(exc.__cause__, URLError):
        return 'transport_or_environment'
    if stage in {'receipt_write', 'receipt_update', 'artifact_write', 'diagnostic_write'} and isinstance(exc, OSError):
        return 'artifact_persistence'
    if isinstance(exc, (ValueError, OSError)) and stage == 'preflight':
        return 'input_validation'
    if isinstance(exc, OSError):
        return 'transport_or_environment'
    return 'auth_expired_or_invalid' if stage == 'authentication' else 'fusion_api_error'


def diagnostic(binding, stage, category, started, *, pid=None, status='BLOCKED',
               process_status=None, http_status=None):
    # Deliberately project a status snapshot, never persist arbitrary ProcessLog
    # text, HTTP bodies or exception messages containing setup credentials.
    result = dict(binding, status=status, stage=stage, failureClass=category,
                  elapsedSeconds=round(max(0, time.monotonic()-started), 3),
                  capturedAt=datetime.now(timezone.utc).isoformat(),
                  artifactRefs=[], errors=[])
    if pid: result['processId'] = pid
    if process_status is not None: result['processStatus'] = process_status
    if isinstance(http_status, int) and 100 <= http_status <= 599:
        result['httpStatus'] = http_status
    actions = {
        'authorization_or_privilege': 'Confirm the selected account and privileges through the core authentication workflow before continuing.',
        'auth_expired_or_invalid': 'Use core authentication recovery with the intended account; never replay an uncertain export POST.',
        'transport_or_environment': 'Check target connectivity. Reconcile the existing receipt/process; do not resubmit the export.',
        'process_timeout': 'Request another read-only check of this same receipt and ProcessId; do not create a replacement export.',
        'process_failed': 'Review the sanitized status snapshot and request the owning shared service diagnostic workflow for this ProcessId; do not resubmit.',
        'artifact_persistence': 'Repair the approved output path. Retain existing receipt/process and reconcile partial files before any retry.',
        'input_validation': 'Correct the selected input, catalog, receipt or output path before continuing.',
        'approval_blocker': 'Obtain immediate approval for the exact export before creating a job.',
        'fusion_api_error': 'Review the HTTP status or task/process identity with the shared export owner; do not repeat an uncertain POST.',
    }
    result['recommendedAction'] = actions[category]
    result['message'] = 'Corporate card export stopped; raw response and credential-bearing logs were not saved.'
    return result


def save_diagnostic(report, receipt, project):
    """Save a new task diagnostic; never overwrite an earlier attempt."""
    path = within(receipt.with_name(receipt.stem+'-diagnostic-'+uuid.uuid4().hex+'.json'), project/'exports')
    saved = dict(report, artifactRefs=[str(path.relative_to(project))])
    with path.open('x') as f: json.dump(saved, f, indent=2)
    report.update(saved)
    return report


def retain_diagnostic(report, receipt, project):
    """Keep the original failure even when its diagnostic cannot be saved."""
    try:
        save_diagnostic(report, receipt, project)
    except (OSError, ValueError):
        report['errors'].append({'failureClass':'artifact_persistence',
                                'message':'Could not save the diagnostic; retain this sanitized report and repair the project path.'})
    return report


def download_export(props, token, scope, pid, args, shared, engine, progress):
    unchanged = progress.get('check_profile', lambda: None)
    unchanged()
    progress['stage'] = 'export_status'
    process, items = shared.engine_wait_for_result(props, token, scope, pid, args.wait_seconds, args.poll_interval)
    unchanged()
    validate_result_identity(process, items, pid, args.task_code)
    if not items and shared.process_completed(process.get('ProcessCompletedFlag')):
        unchanged()
        result = engine.fusion_rest_json(props, engine.result_resource(scope,pid), access_token=token,
                                         query_params={'onlyData':'true'})
        if not isinstance(result, dict) or str(result.get('ProcessId',pid)) != pid:
            raise ValueError('Result identity mismatch')
        items = [result]
        validate_result_identity(process, items, pid, args.task_code)
    current = shared.status_code(items)
    if current != 'COMPLETED':
        terminal = current in shared.ERROR_STATUS_CODES or shared.process_completed(process.get('ProcessCompletedFlag'))
        report = diagnostic(progress['binding'], progress['stage'],
                            'process_failed' if terminal else 'process_timeout', progress['started'],
                            pid=pid, status='FAILED' if terminal else 'PENDING',
                            process_status=current if current in {'COMPLETED_ERRORS','COMPLETED_WARNINGS','ERROR','FAILED','PENDING','RUNNING'} else 'UNKNOWN')
        report['statusSnapshot'] = {'ProcessCompletedFlag': shared.process_completed(process.get('ProcessCompletedFlag')),
                                    'StatusCode': report['processStatus'], 'ProcessId': pid, 'TaskCode': args.task_code}
        report['processLog'] = {'retained': False, 'reason': 'Credential-bearing raw text is not safe to persist; sanitized status snapshot retained instead.'}
        return report, 4 if terminal else 3
    progress['stage'] = 'download_and_sanitize'
    unchanged()
    content, _ = engine.download_result(props,token,scope,pid)
    unchanged()
    safe, report = sanitize(content,args.task_code,args.environment)
    report.update(progress['binding'], status='SANITIZED', processId=pid, capturedAt=datetime.now(timezone.utc).isoformat())
    progress['stage'] = 'artifact_write'
    with args.output.open('xb') as f: f.write(safe)
    with args.output.with_suffix('.evidence.json').open('x') as f: json.dump(report,f,indent=2)
    return report, 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['create','download'])
    parser.add_argument('--properties', type=Path, required=True)
    parser.add_argument('--project-dir', type=Path, required=True)
    parser.add_argument('--task-code', choices=[TASK, ISSUERS, MAPPINGS], default=TASK)
    parser.add_argument('--template-only', action='store_true')
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--approve-export', action='store_true')
    parser.add_argument('--force-login', action='store_true', help='Compatibility option: fresh core OAuth login is always required by this task')
    parser.add_argument('--open-browser', action='store_true', help='Let core open the selected OAuth authorization page')
    parser.add_argument('--environment', help='Exact expected FSM ProcessEnv; required for download')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--wait-seconds', type=int, default=300, help='Bounded status wait, 0 through 300 seconds')
    parser.add_argument('--poll-interval', type=int, default=10, help='Seconds between read-only status checks, 2 through 30')
    args = parser.parse_args()
    progress = {'stage':'preflight', 'started':time.monotonic(),
                'binding':{'taskCode':args.task_code, 'operation':args.operation}}
    project = receipt = None
    pid = None
    try:
        if not 0 <= args.wait_seconds <= 300 or not 2 <= args.poll_interval <= 30:
            raise ValueError('Invalid bounded polling settings')
        repo = Path(__file__).resolve().parents[6]
        project = initialized_project(args.project_dir, repo)
        receipt = within(args.receipt, project/'exports')
        if args.operation == 'create' and (not args.approve_export or receipt.exists()):
            raise ValueError('Fresh export approval and unused receipt required')
        if args.operation == 'download' and (not args.output or not args.environment):
            raise ValueError('Download requires output and expected ProcessEnv')
        shared, create, engine = services()
        # Detect changes during parsing as well as during authentication/requests.
        before = hashlib.sha256(args.properties.read_bytes()).digest()
        props = shared.read_properties(args.properties)
        unchanged = profile_guard(args.properties, props)
        if hashlib.sha256(args.properties.read_bytes()).digest() != before:
            raise ProfileChangedError('Selected authentication profile changed')
        progress['check_profile'] = unchanged
        shared.require_props(props, ['environment','restBaseUrl'])
        # A public core guard validates target syntax before it can be retained.
        from fusion_auth import request_context
        request_context(props)
        scope = shared.task_scope(args.task_code, template_only=args.template_only)
        binding = {'taskCode': args.task_code, 'environment': props['environment'],
                   'restBaseUrl': props['restBaseUrl'].rstrip('/'), 'templateOnly': args.template_only}
        progress['binding'] = dict(binding, operation=args.operation)
        task = create.find_reference_task_by_code(args.task_code)
        if not task or create.csv_export_import_flag(task) != 'Y': raise ValueError('Unsupported or missing catalog task')
        if args.operation == 'download':
            evidence = json.loads(receipt.read_text())
            if any(evidence.get(k) != v for k,v in binding.items()) or evidence.get('status') != 'CREATED':
                raise ValueError('Receipt does not match selected export')
            pid = evidence.get('processId')
            if not isinstance(pid,str) or not re.fullmatch('[1-9][0-9]*',pid): raise ValueError('Invalid receipt process')
            args.output = within(args.output, project/'exports')
            if args.output.exists() or args.output.with_suffix('.evidence.json').exists(): raise ValueError('Existing output')
        progress['stage'] = 'authentication'
        token = acquire_token(shared, props, args, unchanged)
        if args.operation == 'create':
            unchanged()
            progress['stage'] = 'export_create'
            # A POST is attempted once. Authentication errors never replay it.
            report = create_process(props, token, scope, receipt, binding, create.create_export, progress)
            print(json.dumps(report)); return 0
        for attempt in range(2):
            try:
                report, code = download_export(props, token, scope, pid, args, shared, engine, progress)
                break
            except Exception as exc:
                if attempt or getattr(exc, 'status_code', None) not in (401, 403):
                    raise
                unchanged()
                progress['stage'] = 'authentication'
                token = acquire_token(shared, props, args, unchanged, refresh=True)
        if code:
            progress['stage'] = 'diagnostic_write'
            retain_diagnostic(report, receipt, project)
        print(json.dumps(report)); return code
    except Exception as exc:
        category = ('approval_blocker' if progress['stage']=='preflight' and args.operation=='create' and not args.approve_export
                    else failure_class(exc, progress['stage']))
        report = diagnostic(progress['binding'], progress['stage'], category, progress['started'],
                            pid=pid or progress.get('processId'), http_status=getattr(exc,'status_code',None))
        if isinstance(exc, ProfileChangedError):
            report.update(blockerCode='SELECTED_PROFILE_CHANGED',
                          message='The selected authentication configuration changed; restart preflight with the intended profile. Do not replay an uncertain POST.')
        if project is not None and receipt is not None:
            retain_diagnostic(report, receipt, project)
        print(json.dumps(report)); return 2


if __name__ == '__main__': raise SystemExit(main())
