#!/usr/bin/env python3
"""Validate sanitized FSCR evidence and render local HTML/JSON; never call Fusion."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract_validation import validate, ContractError

ROOT = Path(__file__).resolve().parents[4]
SKILL = 'core.validation.reporting'
SYS_SKILLS = ROOT / 'core/project-mgmt/scripts'
sys.path.insert(0, str(SYS_SKILLS))
from token_usage_logger import append_token_usage_log  # noqa: E402


class InputError(ValueError):
    pass


def dump(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def loads(content):
    def reject_constant(_value):
        raise InputError('non-finite JSON numbers are not permitted')
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InputError('duplicate JSON keys are not permitted')
            result[key] = value
        return result
    return json.loads(content, parse_constant=reject_constant, object_pairs_hook=unique_keys)


def load(path):
    return loads(Path(path).read_text(encoding='utf-8'))


def validate_schema(value, name):
    schema = load(ROOT / 'schemas' / name)
    try:
        validate(value, schema)
    except ContractError as error:
        raise InputError(f'{name}: {error}') from None


def unique(items, field):
    values = [item[field] for item in items]
    if len(values) != len(set(values)):
        raise InputError(f'duplicate {field}')


def assess(data):
    """Derive readiness conservatively without asserting that supplied evidence is true."""
    validate_schema(data, 'implementation-validation-run.schema.json')
    for items, field in [(data['requirements'], 'requirement_id'), (data['tasks'], 'task_id'),
                         (data['checks'], 'result_id')]:
        unique(items, field)
    # One snapshot per check in one run. Historical runs remain separate artifacts.
    unique(data['checks'], 'check_id')
    requirements = {x['requirement_id']: x for x in data['requirements']}
    tasks = {x['task_id']: x for x in data['tasks']}
    checks = {x['check_id']: x for x in data['checks']}
    gaps, blockers, followups = [], [], []
    for task in tasks.values():
        if task['environment'] != data['environment']:
            raise InputError('task environment differs from run environment')
    for req in requirements.values():
        if any(t not in tasks for t in req['task_refs']):
            raise InputError('requirement refers to an unknown task')
        if req['required'] and (not req['task_refs'] or not req['check_ids']):
            gaps.append(f"{req['requirement_id']}: incomplete requirement-to-task/check mapping")
        for check_id in req['check_ids']:
            check = checks.get(check_id)
            if check is None:
                gaps.append(f"{req['requirement_id']}: check {check_id} has no result")
            elif req['requirement_id'] not in check['requirement_refs']:
                raise InputError('requirement/check traceability is not reciprocal')
            elif req['required'] and not check['required']:
                raise InputError('required requirement mapped to an optional check')
    for check in checks.values():
        if check['environment'] != data['environment']:
            raise InputError('check environment differs from run environment')
        if any(ref not in requirements for ref in check['requirement_refs']):
            raise InputError('check refers to an unknown requirement')
        if any(ref not in tasks for ref in check['task_refs']):
            raise InputError('check refers to an unknown task')
        if any(check['check_id'] not in requirements[ref]['check_ids'] for ref in check['requirement_refs']):
            raise InputError('check/requirement traceability is not reciprocal')
        unique(check['assertions'], 'assertion_id')
        state = check['status']
        if state != 'PASS' and not check['reason'].strip():
            raise InputError('non-pass check needs a reason')
        if state in {'PASS', 'FAIL'} and check['method'] == 'none':
            raise InputError('observed outcome needs a verification method')
        if state == 'PASS':
            if not check['assertions'] or any(a['status'] != 'PASS' or not a['observed'].strip()
                                           or not a['evidence_refs'] for a in check['assertions']):
                raise InputError('PASS requires observed passing assertions and evidence references')
        if state in {'SKIPPED', 'NOT_RUN', 'NOT_APPLICABLE', 'BLOCKED'} and any(
                a['status'] == 'PASS' for a in check['assertions']):
            raise InputError('unexecuted check cannot contain passing assertions')
        if check['method'] in {'manual-evidence', 'user-attestation'} and not check['performed_by'].strip():
            raise InputError('manual result needs performer attribution')
        if check['blocking'] and state in {'FAIL', 'BLOCKED', 'INDETERMINATE'}:
            blockers.append(f"{check['check_id']}: {state}")
        if state in {'FAIL', 'INDETERMINATE'}:
            gaps.append(f"{check['check_id']}: unresolved {state}")
        if check['required'] and (state not in {'PASS', 'NOT_APPLICABLE'} or
                                 not check['evidence_current'] or check['method'] == 'user-attestation'):
            gaps.append(f"{check['check_id']}: required verification incomplete, stale or attested only")
        if check['next_action']:
            followups.append(f"{check['owner']}: {check['next_action']}")
        tx = check.get('transaction')
        if data['stage'] == 'implementation-review' and tx:
            raise InputError('setup review cannot contain transaction execution')
        if tx:
            if tx['new_primary_count'] is None and state != 'INDETERMINATE':
                raise InputError('unknown creation count requires INDETERMINATE')
            if state == 'PASS' and (not tx['record_id'] or (tx['new_primary_count'] == 0 and not tx['reused'])):
                raise InputError('transaction PASS needs a created or explicitly reused record')
            if (tx['new_primary_count'] == 1 or tx['reused']) and tx['cleanup_status'] == 'not-needed':
                raise InputError('created or reused test data needs explicit cleanup or retention disposition')
            if tx['reused'] and tx['new_primary_count'] != 0:
                raise InputError('reused record cannot also be a new creation')
            if state in {'SKIPPED', 'NOT_RUN', 'NOT_APPLICABLE', 'BLOCKED'} and tx['new_primary_count'] != 0:
                raise InputError('unexecuted check cannot have created records')
            if tx['new_primary_count'] == 1 and not tx['record_id'] and state != 'INDETERMINATE':
                raise InputError('known new transaction needs its record identity')
            if (tx['new_primary_count'] != 0 or tx['reused']) and not tx['approval_ref']:
                raise InputError('transaction execution needs an approval reference')
            if tx['cleanup_status'] == 'removed-verified' and not tx['cleanup_evidence_refs']:
                raise InputError('verified cleanup needs evidence')
            if tx['cleanup_status'] in {'pending','failed','unknown'}:
                gaps.append(f"{check['check_id']}: cleanup {tx['cleanup_status']}")
                if not tx['cleanup_next_action']:
                    raise InputError('unresolved cleanup needs a next action')
            if tx['cleanup_status'] == 'retained' and not tx['cleanup_next_action']:
                raise InputError('retention needs a rationale and owner')
    if data['stage'] == 'transactional-validation':
        if len(checks) != 1:
            raise InputError('a transactional invocation must record exactly one selected check')
        check = next(iter(checks.values()))
        if check['status'] in {'PASS','FAIL','INDETERMINATE'} and not check.get('transaction'):
            raise InputError('executed transactional check needs transaction and cleanup evidence')
    else:
        if not requirements:
            gaps.append('No approved requirements mapped')
        for task in tasks.values():
            if task['status'] not in {'completed','not-applicable'} or not task['evidence_current']:
                gaps.append(f"{task['task_id']}: task incomplete or evidence stale")
    if not checks:
        gaps.append('No checks recorded')
    if data['stage'] == 'transactional-validation' and not any(c['status'] == 'PASS' for c in checks.values()):
        gaps.append('No passing transaction observed in this invocation')
    if data['errors']:
        gaps.append('Unresolved diagnostics require review')
    # Every declared required requirement needs at least one applicable verified check.
    for req in requirements.values():
        if req['required'] and req['check_ids'] and all(
                checks.get(c, {}).get('status') == 'NOT_APPLICABLE' for c in req['check_ids']):
            gaps.append(f"{req['requirement_id']}: no applicable verification")
    status_counts = {s: sum(c['status'] == s for c in checks.values()) for s in
                     ['PASS','FAIL','BLOCKED','INDETERMINATE','SKIPPED','NOT_RUN','NOT_APPLICABLE']}
    return {'readiness': 'BLOCKED' if blockers else 'NEEDS_REVIEW' if gaps else 'READY_WITHIN_VERIFIED_SCOPE',
            'readiness_scope': data['stage'], 'counts': status_counts,
            'requirement_count': len(requirements), 'task_count': len(tasks),
            'gaps': gaps, 'blockers': blockers, 'followups': followups}


def render(data, assessment):
    """Present the recorded assessment without collecting evidence or changing its meaning."""
    def esc(value):
        if value is None:
            return 'Unknown'
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        return html.escape(str(value), quote=True)

    def table(headers, rows):
        return '<div class="table-wrap"><table><thead><tr>' + ''.join(
            f'<th scope="col">{esc(h)}</th>' for h in headers
        ) + '</tr></thead><tbody>' + ''.join(
            '<tr>' + ''.join(f'<td>{esc(v)}</td>' for v in row) + '</tr>' for row in rows
        ) + '</tbody></table></div>'

    def items(values, empty):
        return '<ul>' + ''.join(f'<li>{esc(v)}</li>' for v in values) + '</ul>' if values else f'<p>{esc(empty)}</p>'

    def metric(value, label, note='', tone=''):
        return (f'<div class="metric {tone}"><strong>{esc(value)}</strong><span>{esc(label)}</span>'
                f'<small>{esc(note)}</small></div>')

    def freshness(check):
        return 'Current (as supplied)' if check['evidence_current'] else 'Stale or unconfirmed'

    def method(check):
        return {'api': 'API evidence', 'artifact': 'Recorded artifact evidence',
                'manual-evidence': 'Manual evidence', 'user-attestation': 'User attestation only',
                'none': 'No verification performed'}[check['method']]

    def assertion_table(check):
        return table(['Assertion', 'Expected', 'Observed', 'Result', 'Evidence references'],
                     [(a['assertion_id'], a['expected'], a['observed'] or 'Not observed',
                       a['status'], a['evidence_refs'] or 'No evidence supplied')
                      for a in check['assertions']]) if check['assertions'] else '<p>No assertions supplied.</p>'

    title = data['stage'].replace('-', ' ').title()
    counts = {state: sum(c['status'] == state for c in data['checks']) for state in
              ['PASS', 'FAIL', 'BLOCKED', 'INDETERMINATE', 'SKIPPED', 'NOT_RUN', 'NOT_APPLICABLE']}
    completed = sum(t['status'] == 'completed' for t in data['tasks'])
    body = (f'<header><div class="eyebrow">FSCR / Validation</div><h1>{esc(title)}</h1>'
            f'<p class="metadata">{esc(data["project_id"])} · {esc(data["environment"])} · '
            f'{esc(data["started_at"])}</p></header>')

    def completion(task):
        if task['status'] == 'completed':
            return task.get('completed_at') or 'Not recorded'
        return 'Not applicable' if task['status'] == 'not-applicable' else 'Not completed'

    body += '<section class="panel"><h2>Run Book tasks</h2>'
    if data['tasks']:
        body += (f'<p>{len(data["tasks"])} recorded tasks · {completed} marked completed. '
                 'Task completion and verified setup correctness are separate.</p>')
        body += table(['Task ID', 'Task', 'Source status', 'Completed at (source timezone)'],
                      [(t['task_id'], t['title'], t['status'], completion(t)) for t in data['tasks']])
    else:
        body += '<p>No Run Book task evidence supplied. Task completion has not been verified.</p>'
    body += '</section><section class="panel"><h2>Scope and readiness</h2>'
    readiness_text = {
        'READY_WITHIN_VERIFIED_SCOPE': 'Ready within the stated stage and supplied evidence.',
        'NEEDS_REVIEW': 'Evidence gaps or unresolved actions need review.',
        'BLOCKED': 'Blocking findings remain in this assessment.',
    }[assessment['readiness']]
    tone = {'READY_WITHIN_VERIFIED_SCOPE': 'positive', 'NEEDS_REVIEW': 'caution', 'BLOCKED': 'negative'}[assessment['readiness']]
    body += (f'<div class="decision {tone}"><strong>{esc(assessment["readiness"])}</strong>'
             f'<p>{esc(readiness_text)}</p></div>')
    body += '<div class="metrics scope-metrics">' + metric(len(data['checks']), 'Recorded checks') + \
            metric(len(data['requirements']), 'Requirements', 'Mapped scope, not a verification percentage') + \
            metric(len(data['tasks']), 'Run Book tasks', f'{completed} marked completed') + '</div>'
    status_labels = [('PASS', 'Passed', 'positive'), ('FAIL', 'Failed', 'negative'),
                     ('BLOCKED', 'Blocked', 'caution'), ('INDETERMINATE', 'Unknown outcome', 'caution'),
                     ('SKIPPED', 'Skipped', ''), ('NOT_RUN', 'Not run', ''), ('NOT_APPLICABLE', 'Not applicable', '')]
    body += '<div class="metrics status-metrics">' + ''.join(
        metric(counts[state], label, state, state_tone) for state, label, state_tone in status_labels
    ) + '</div>'
    body += ('<p class="note">Counts describe this run only. They count checks, not tasks, records or distinct defects. '
             'A recorded PASS may still be stale or attested only; use the readiness decision and evidence details. '
             'Readiness does not approve release or authorize execution.</p>')
    body += table(['Scope field', 'Value'], [(label, data[key]) for label, key in [
        ('Run ID', 'run_id'), ('Stage', 'stage'), ('Request', 'request'), ('Scope', 'scope'),
        ('Approved scope reference', 'scope_ref'), ('Requirement version', 'requirement_version')]])
    body += '</section><section><h2>Findings and next actions</h2><div class="columns">'
    body += '<div class="panel"><h3>Blocking findings</h3>' + items(
        assessment['blockers'], 'No blocking findings recorded. This is not independent verification.'
    ) + '</div><div class="panel"><h3>Gaps and unresolved evidence</h3>' + items(
        assessment['gaps'], 'No assessment gaps recorded within this scope.'
    ) + '</div></div>'
    attention = [c for c in data['checks'] if c['status'] != 'PASS' or not c['evidence_current']
                 or c['method'] == 'user-attestation' or c['next_action']]
    cleanup_followups = []
    for check in data['checks']:
        tx = check.get('transaction')
        if tx and tx['cleanup_status'] in {'pending', 'failed', 'unknown'}:
            cleanup_followups.append(
                f"{check['check_id']}: cleanup {tx['cleanup_status']} — "
                f"{tx['cleanup_owner']}: {tx['cleanup_next_action']}")
    if attention:
        body += table(['Check', 'Recorded result', 'Evidence state', 'Reason', 'Owner', 'Next action'], [
            (c['check_id'] + ' — ' + c['title'], c['status'], freshness(c),
             c['reason'] or 'See assessment and assertion evidence.', c['owner'],
             c['next_action'] or 'No next action recorded.') for c in attention])
    elif not cleanup_followups:
        body += '<p>No check-specific follow-up recorded.</p>'
    body += '<h3>Recorded follow-up actions</h3>' + items(
        assessment['followups'] + cleanup_followups, 'No check follow-up actions supplied.'
    ) + '</section><section class="panel"><h2>Requirements and coverage</h2>'
    body += table(['Requirement ID', 'Requirement', 'Expected setup', 'Tasks', 'Checks', 'Required', 'Owner', 'Source'], [
        (r['requirement_id'], r['description'], r['expected_setup'], r['task_refs'], r['check_ids'],
         r['required'], r['owner'], r['source_ref']) for r in data['requirements']])
    body += ('<p class="note">A requirement-to-task/check mapping is traceability, not proof that its expected values '
             'were saved. Missing, stale, skipped and unrun verification remains visible in the assessment.</p></section>')
    body += '<section class="panel"><h2>Task and load evidence</h2>' + table(
        ['Task', 'Source status', 'Evidence captured', 'Current (as supplied)', 'Details', 'Owner', 'Source'], [
            (t['title'], t['status'], t['captured_at'], t['evidence_current'],
             t['details'], t['owner'], t['source_ref']) for t in data['tasks']]) + '</section>'
    body += '<section><h2>Check evidence</h2><p class="note">Evidence references are inert text. The report displays '
    body += 'supplied observations; it does not retrieve their sources or independently confirm their truth.</p>'
    for c in data['checks']:
        body += f'<article class="panel check"><h3>{esc(c["title"])} — {esc(c["status"])}</h3>'
        body += (f'<p class="provenance">{esc(method(c))} · {esc(freshness(c))} · '
                 f'Owner: {esc(c["owner"])}</p>')
        if c['method'] in {'manual-evidence', 'user-attestation'}:
            body += f'<p>Performed or attested by: {esc(c["performed_by"])}.</p>'
        if c['method'] == 'user-attestation':
            body += '<p class="note">User attestation alone does not establish verified readiness.</p>'
        body += table(['Check field', 'Recorded value'], [(k, c[k]) for k in c if k not in {'assertions', 'transaction'}])
        body += '<h4>Expected versus observed</h4>' + assertion_table(c)
        if 'transaction' in c:
            tx = c['transaction']
            # A missing count is not zero. A known count alone does not prove cleanup.
            created = tx['new_primary_count']
            if tx['cleanup_status'] == 'removed-verified' and created is not None:
                retained = 0
            elif tx['cleanup_status'] == 'retained' and (created == 1 or tx['reused']):
                retained = 1
            elif tx['cleanup_status'] == 'not-needed' and created == 0 and not tx['reused']:
                retained = 0
            else:
                retained = None
            body += '<h4>Transaction and cleanup</h4><div class="metrics scope-metrics">'
            body += metric(created, 'New primary records', 'Unknown is not zero')
            body += metric('Yes' if tx['reused'] else 'No', 'Existing record reused')
            body += metric(retained, 'Primary test records retained', 'Only as established by the recorded disposition')
            body += '</div>'
            body += (f'<p><strong>Cleanup disposition: {esc(tx["cleanup_status"])}</strong> · '
                     f'Owner: {esc(tx["cleanup_owner"])}</p>'
                     '<p class="note">Transaction outcome and cleanup are separate. Record evidence before cleanup; '
                     'a missing screenshot or verification is never implied by a successful test.</p>')
            body += table(['Transaction field', 'Recorded value'], list(tx.items()))
        body += '</article>'
    body += '</section><section class="panel"><h2>Decisions</h2>' + table(
        ['Decision', 'Summary', 'Owner', 'Source'],
        [(d['decision_id'], d['summary'], d['owner'], d['source_ref']) for d in data['decisions']])
    body += '</section><section class="panel"><h2>Recommendations</h2>' + table(
        ['Recommendation', 'Owner', 'Source'],
        [(r['message'], r['owner'], r['source_ref']) for r in data['recommendations']])
    body += '</section><section class="panel"><h2>Limitations</h2>' + items(
        data['limitations'], 'No additional limitations supplied. Evidence collection and validation remain outside this renderer.'
    ) + '</section><section class="panel"><h2>Errors</h2>'
    body += table(['Stage', 'Failure class', 'Message', 'Recommended action', 'Artifact references', 'External IDs'], [
        (e['stage'], e['failure_class'], e['message'], e['recommended_action'], e['artifact_refs'], e['external_ids'])
        for e in data['errors']]) if data['errors'] else '<p>No diagnostics supplied.</p>'
    body += '</section><footer>FSCR validation · Single-run evidence report · No live operations performed by this renderer.</footer>'
    css = '''
:root{--ink:#19333c;--muted:#53656a;--line:#d9e1df;--paper:#f3f5f2;--teal:#236c60}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:1280px;margin:auto;padding:32px 24px 56px}header{padding:10px 0 20px;border-bottom:4px solid var(--teal)}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:800;color:var(--teal)}
h1{font-size:clamp(28px,4vw,44px);line-height:1.15;margin:12px 0}h2{font-size:25px;line-height:1.25;margin:0 0 14px}
h3{font-size:20px;margin:0 0 12px}h4{font-size:17px;margin:24px 0 10px}p{margin:10px 0 16px}
section{margin-top:28px}.panel{padding:24px;background:#fff;border:1px solid var(--line);border-radius:10px}
.metadata,.note,footer{color:var(--muted)}.note{font-size:14px}.decision{padding:18px 20px;border-left:5px solid var(--teal);background:#edf5f0}
.decision.negative{border-color:#a43d32;background:#fff0eb}.decision.caution{border-color:#976b1d;background:#fff6df}
.decision strong{font-size:21px;overflow-wrap:anywhere}.decision p{margin-bottom:0}
.metrics{display:grid;gap:12px;margin:20px 0}.scope-metrics{grid-template-columns:repeat(3,minmax(0,1fr))}
.status-metrics{grid-template-columns:repeat(7,minmax(0,1fr))}.metric{padding:16px;border:1px solid var(--line);border-radius:8px;background:#fff}
.metric strong{font-size:32px;line-height:1.1;display:block;overflow-wrap:anywhere}.metric span{display:block;font-weight:700;font-size:14px;margin-top:9px}
.metric small{display:block;font-size:11px;color:var(--muted);margin-top:6px;overflow-wrap:anywhere}
.metric.positive strong{color:#236c60}.metric.negative strong{color:#a43d32}.metric.caution strong{color:#856014}
.columns{display:grid;grid-template-columns:1fr 1fr;gap:18px}.check{margin-top:18px}.provenance{font-weight:650;color:var(--teal)}
ul{padding-left:22px}li{margin:8px 0;overflow-wrap:anywhere}.table-wrap{overflow-x:auto;margin:16px 0 4px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere}
th{background:#eef3f0;color:#42595e;font-size:12px}td{max-width:400px}footer{font-size:12px;margin-top:30px}
@media(max-width:850px){.status-metrics{grid-template-columns:repeat(3,minmax(0,1fr))}.columns{grid-template-columns:1fr}}
@media(max-width:520px){main{padding:20px 12px}.panel{padding:16px}.scope-metrics,.status-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}table{min-width:640px}}
@media print{body{background:#fff;font-size:11px}main{max-width:none;padding:0}.panel{border-radius:0;padding:14px}.table-wrap{overflow:visible}
table{font-size:10px}th,td{padding:7px;max-width:none}.metric{padding:10px}.metric strong{font-size:24px}.metrics,.decision{break-inside:avoid}h2,h3,h4{break-after:avoid}}
'''
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title><style>{css}</style></head><body><main>{body}</main></body></html>\n')


def safe_project(root, project_id):
    project_base = root / 'project'
    # Do not turn a redirected project directory into the trusted output root.
    if project_base.is_symlink() or project_base.resolve().parent != root.resolve():
        raise InputError('unsafe project base path')
    project = project_base / project_id
    if project.is_symlink() or project.resolve().parent != project_base.resolve() or project.name == '_template':
        raise InputError('unsafe project path')
    if not (project / 'state/project-state.json').is_file():
        raise InputError('initialize and select an existing project before publication')
    return project


def safe_target(project, relative):
    path = project / relative
    if not path.resolve().is_relative_to(project.resolve()):
        raise InputError('output escapes project')
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise InputError('symlink output is not permitted')
        if part == project.parent:
            break
    return path


def publish_bundle(*, project_id, run_id, started_at, bodies, input_refs, notes,
                   input_tokens, files_read, root=ROOT):
    """Publish a new run, index, state and token record; rollback on handled write failure."""
    # Only simple paired HTML/JSON filenames and an unused safe directory are accepted.
    import re
    if not isinstance(run_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,119}', run_id):
        raise InputError('unsafe report run identity')
    if (len(bodies) != 2 or any(not re.fullmatch(r'[a-z0-9-]+\.(html|json)', name) for name in bodies)
            or {Path(name).suffix for name in bodies} != {'.html', '.json'}
            or len({Path(name).stem for name in bodies}) != 1):
        raise InputError('report publication requires a matching HTML/JSON pair')
    project = safe_project(root, project_id)
    folder = safe_target(project, f'artifacts/shared/validation/{run_id}')
    record_path = safe_target(project, f'state/runs/{run_id}.json')
    state_path = safe_target(project, 'state/project-state.json')
    index_path = safe_target(project, 'artifacts/artifact-index.json')
    token_path = safe_target(project, 'artifacts/shared/token-usage/current/token-usage-log.md')
    lock_path = safe_target(project, 'state/.validation-report.lock')
    if folder.exists() or record_path.exists():
        raise InputError('run already exists; use a new run_id, never overwrite history')
    snapshots = {}
    created_folder = False
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        state, index = load(state_path), load(index_path)
        if state['project_id'] != project_id or index['project_id'] != project_id:
            raise InputError('project identity mismatch')
        expected_index = f'project/{project_id}/artifacts/artifact-index.json'
        if state['artifact_index_ref'] != expected_index:
            raise InputError('unsupported artifact index reference')
        # Validate existing records individually; the index schema uses a local $ref.
        validate_schema({k:v for k,v in state.items() if k != '$schema'}, 'project-state.schema.json')
        if set(index) - {'$schema'} != {'project_id','updated_at','artifacts'} or not isinstance(index['artifacts'],list):
            raise InputError('invalid artifact index')
        for item in index['artifacts']:
            validate_schema(item, 'project-artifact.schema.json')
        for path in [state_path,index_path,record_path,token_path]:
            snapshots[path] = path.read_bytes() if path.exists() else None
        report_path = folder / next(name for name in bodies if name.endswith('.html'))
        result_path = folder / next(name for name in bodies if name.endswith('.json'))
        timestamp = datetime.now(timezone.utc).isoformat()
        contents = {folder / name: content for name, content in bodies.items()}
        references = [str(p.relative_to(root)) for p in contents]
        ids = {item['artifact_id'] for item in index['artifacts']}
        for path, content in contents.items():
            artifact_id = f'{run_id}-{path.suffix[1:]}'
            if artifact_id in ids:
                raise InputError('artifact identity already exists')
            item = {'artifact_id':artifact_id,'name':path.name,
                    'artifact_type':'report' if path.suffix == '.html' else 'validation_result',
                    'skill_id':SKILL,'location':str(path.relative_to(root)),'version':'1.0.0','status':'draft',
                    'created_at':timestamp,'updated_at':timestamp,'checksum':hashlib.sha256(content.encode()).hexdigest()}
            validate_schema(item, 'project-artifact.schema.json')
            index['artifacts'].append(item)
        index['updated_at'] = timestamp
        output_tokens = sum(len(content)//4 for content in contents.values())
        usage = {'estimation_method':'chars/4 estimate; sanitized report input and report bodies only',
                 'estimated_input_tokens':input_tokens,'estimated_output_tokens':output_tokens,
                 'estimated_total_tokens':input_tokens+output_tokens,'artifacts_written':2,'files_read':files_read,
                 'log_ref':str(token_path.relative_to(root)),
                 'notes':'Does not estimate upstream analysis or API work; record those in their owning runs.'}
        record = {'run_id':run_id,'skill_id':SKILL,'started_at':started_at,'completed_at':timestamp,
                  'status':'completed','inputs':input_refs,'outputs':list(bodies), 'artifact_refs':references,
                  'token_usage':usage,'notes':notes}
        validate_schema(record,'skill-run.schema.json')
        state['updated_at'] = timestamp
        state['latest_run_ref'] = str(record_path.relative_to(root))
        # Do not modify implementation completion status or active execution route.
        contents.update({record_path:dump(record),index_path:dump(index),state_path:dump(state)})
        folder.mkdir(parents=True, exist_ok=False)
        created_folder = True
        for path, content in contents.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            fd, temp = tempfile.mkstemp(prefix='.validation-', dir=path.parent)
            try:
                with os.fdopen(fd,'w',encoding='utf-8') as stream:
                    stream.write(content)
                os.replace(temp,path)
            finally:
                if os.path.exists(temp): os.unlink(temp)
        append_token_usage_log(project_id=project_id,skill_id=SKILL,task='Publish validation report',
            trigger='Explicit validation/report request',activity_start_time=started_at,
            artifact_paths=[report_path,result_path],files_read=files_read,estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,notes=usage['notes'],root=root)
        return {'report':str(report_path),'result':str(result_path),'run_record':str(record_path),
                'token_usage':usage}
    except Exception:
        if created_folder:
            shutil.rmtree(folder)
        for path, original in snapshots.items():
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    finally:
        os.close(lock_fd)
        lock_path.unlink(missing_ok=True)


def publish(data, assessment, root=ROOT):
    """Publish one assessed run using the common local artifact writer."""
    result = publish_bundle(project_id=data['project_id'], run_id=data['run_id'],
        started_at=data['started_at'], bodies={data['stage'] + '.html': render(data, assessment),
            data['stage'] + '.json': dump({'run': data, 'assessment': assessment})},
        input_refs=[data['scope_ref']], notes='Report generation completed; business readiness: ' + assessment['readiness'],
        input_tokens=max(1, len(dump(data)) // 4), files_read=1, root=root)
    return {**result, 'readiness': assessment['readiness']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--input',type=Path,help='Sanitized implementation-validation-run JSON')
    source.add_argument('--check-definition',type=Path,help='Validate a normalized pillar definition without executing it')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run',action='store_true',help='Validate and assess; no files or network calls')
    mode.add_argument('--publish',action='store_true',help='Write a new report run to its existing repository project')
    args = parser.parse_args()
    if args.check_definition and (args.publish or args.dry_run):
        parser.error('--check-definition cannot be combined with report modes')
    if args.input and not (args.publish or args.dry_run):
        parser.error('--input requires --dry-run or --publish')
    try:
        if args.check_definition:
            definition = load(args.check_definition)
            validate_schema(definition, 'implementation-validation-check.schema.json')
            if not definition['assertions'] or not definition['prerequisites']:
                raise InputError('check definition needs assertions and prerequisites')
            if definition['execution']['poll_interval_seconds'] > definition['execution']['timeout_seconds']:
                raise InputError('poll interval exceeds timeout')
            print(dump({'status':'valid-definition','execution_authorized':False}))
            return 0
        data = load(args.input)
        assessment = assess(data)
        if args.dry_run:
            print(dump({'mode':'dry-run','assessment':assessment}))
        else:
            print(dump(publish(data,assessment)))
        # Generation success is distinct from business success; preserve reports for negative outcomes.
        if assessment['counts']['INDETERMINATE']: return 3
        if assessment['counts']['FAIL']: return 4
        return 0 if assessment['readiness'] == 'READY_WITHIN_VERIFIED_SCOPE' else 2
    except (InputError, ValueError, KeyError) as error:
        print(dump({'status':'failed','stage':'input','failure_class':'input_validation',
                    'message': str(error) if isinstance(error,InputError) else 'Malformed input or project metadata',
                    'recommended_action':'Correct sanitized input and rerun dry-run.'}),file=sys.stderr)
        return 1
    except OSError:
        print(dump({'status':'failed','stage':'publication','failure_class':'artifact_persistence',
                    'message':'Project publication failed; inspect permissions, existing run and lock state.',
                    'recommended_action':'Reconcile local artifacts before retrying; no Fusion operation was attempted.'}),file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
