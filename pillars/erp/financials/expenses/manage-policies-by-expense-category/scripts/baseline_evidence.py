"""Validate host-recorded declared-route baseline evidence; never authorizes writes."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from workbook_intake import IntakeError, TASK


def digest(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise IntakeError('Missing or unsafe baseline evidence file')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    digest(path)
    if Path(path).stat().st_size > 1024 * 1024:
        raise IntakeError('Baseline evidence record is too large')
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise IntakeError('Baseline evidence record must be an object')
    return value


def verify(baseline, receipt_path, plan_path, approval_path, environment, process_id):
    if not isinstance(process_id, str) or re.fullmatch(r'[1-9][0-9]*', process_id) is None:
        raise IntakeError('Positive baseline export process ID required')
    if not all([receipt_path, plan_path, approval_path, environment]):
        raise IntakeError('Declared-route baseline receipt, export plan and approval required')
    receipt, plan, approval = [record(p) for p in [receipt_path, plan_path, approval_path]]
    body = {'TaskCode': TASK, 'SetupTaskCSVExportProcess': [{'TaskCode': TASK}]}
    endpoint = '/fscmRestApi/resources/11.13.18.05/setupTaskCSVExports'
    for value in [plan, approval]:
        if value.get('method') != 'POST' or value.get('path') != endpoint or value.get('body') != body or value.get('environment') != environment:
            raise IntakeError('Baseline evidence must identify the exact approved task data export')
        for key in ['importApproved', 'import_approved', 'newImportApproved',
                    'validationWaiverGranted', 'validation_waiver_granted', 'repairReplayCleanupApproved']:
            if value.get(key, False) is not False:
                raise IntakeError('Baseline export evidence cannot grant import or waiver authority')
    origin = plan.get('origin', '')
    if not isinstance(origin, str):
        raise IntakeError('Safe HTTPS baseline origin required')
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.path not in {'', '/'} or parsed.query or parsed.fragment:
        raise IntakeError('Safe HTTPS baseline origin required')
    plan_sha, approval_sha = digest(plan_path), digest(approval_path)
    if not (receipt.get('recordedFrom') == 'observed-declared-route-result'
            and receipt.get('processId') == process_id and receipt.get('taskCode') == TASK
            and receipt.get('environment') == environment and receipt.get('origin') == origin
            and receipt.get('completed') is True and receipt.get('retrieved') == 'FileContent'
            and receipt.get('artifactSha256') == digest(baseline)
            and receipt.get('artifactBytes') == Path(baseline).stat().st_size
            and receipt.get('exportPlanSha256') == plan_sha
            and receipt.get('approvalSha256') == approval_sha
            and approval.get('planSha256') == plan_sha):
        raise IntakeError('Baseline download process/bytes/approval bindings mismatch')
    return {'kind': 'host_recorded_declared_route', 'process_id': process_id,
            'environment': environment, 'origin': origin,
            'receipt_sha256': digest(receipt_path), 'export_plan_sha256': plan_sha,
            'export_approval_sha256': approval_sha,
            'authority_boundary': 'Local audit evidence, not independent authentication, freshness proof or import approval.'}
