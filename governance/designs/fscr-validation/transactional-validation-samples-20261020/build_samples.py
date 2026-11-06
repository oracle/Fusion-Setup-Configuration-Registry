#!/usr/bin/env python3
"""Build an offline synthetic report pack with the framework's real renderers."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
DISCLAIMER = 'SYNTHETIC SAMPLE — no Fusion access, real approvals, transaction creation or deletion occurred.'
CASES = [
    ('01-pass-cleanup-verified', 'Passed · cleanup verified', 'PASS', 'removed-verified', 'READY_WITHIN_VERIFIED_SCOPE',
     'The narrow transaction assertions pass and removal is evidenced.'),
    ('02-pass-cleanup-pending', 'Passed · cleanup pending', 'PASS', 'pending', 'NEEDS_REVIEW',
     'The transaction passes; a named owner must still handle cleanup.'),
    ('03-blocked-prerequisite', 'Blocked before execution', 'BLOCKED', 'not-needed', 'BLOCKED',
     'A required reference is unavailable. No transaction is attempted.'),
    ('04-business-assertion-failed', 'Created · business assertion failed', 'FAIL', 'removed-verified', 'BLOCKED',
     'Creation succeeds, but a stored value differs from the approved expectation.'),
    ('05-user-skipped', 'User skipped the check', 'SKIPPED', 'not-needed', 'NEEDS_REVIEW',
     'The user bypasses this check. Its scope remains unverified.'),
    ('06-unknown-outcome', 'Unknown creation outcome', 'INDETERMINATE', 'unknown', 'BLOCKED',
     'A timeout leaves creation uncertain. Reconcile before another attempt.'),
]
CSS = '''*{box-sizing:border-box}body{margin:0;background:#f2f3ee;color:#233c35;font:16px/1.55 system-ui,-apple-system,sans-serif}main{max-width:1240px;margin:auto;padding:32px 24px}header{background:#173e35;color:white;padding:38px;border-radius:14px}h1{font-size:clamp(30px,4vw,48px);line-height:1.1;margin:12px 0 18px}h2{font-size:25px;margin:0 0 14px}h3{font-size:20px;margin:12px 0}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:12px;font-weight:700}.tag{display:inline-block;padding:5px 10px;background:#e7eee8;border-radius:4px;font-weight:700;font-size:13px}.notice{padding:18px 22px;background:#fff4d8;border-left:5px solid #b38122;margin:22px 0}.metrics,.cards{display:grid;gap:16px}.metrics{grid-template-columns:repeat(4,minmax(0,1fr));margin:22px 0}.metric{padding:20px;background:#fff;border:1px solid #d9e0d7;border-radius:9px}.metric b{font-size:38px;display:block}.metric span{font-size:14px}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}section{margin:28px 0;padding:26px;background:white;border:1px solid #d9e0d7;border-radius:10px}article{border:1px solid #d9e0d7;border-radius:9px;padding:24px;background:#fcfcf9}a{color:#195e4b;text-underline-offset:3px}.button{display:inline-block;border:1px solid #1d6753;padding:9px 14px;border-radius:6px;font-weight:700;margin:5px 10px 5px 0;text-decoration:none}.meta{color:#52665c;font-size:14px}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #dde3dc}th{background:#eef2eb}code{font-size:13px;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere}.scroll{overflow-x:auto}footer{padding:20px 0;color:#52665c}@media(max-width:720px){main{padding:14px}.metrics,.cards{grid-template-columns:1fr}header,section{padding:22px}table{min-width:620px}}@media print{body{background:white}main{padding:0}header{color:#173e35;background:white}article{break-inside:avoid}.cards{display:block}article{margin:12px 0}.button{border:0;padding:0}table{min-width:0}}'''


def document(title, body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
            f'<title>{html.escape(title)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>\n')


def dump(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def badge(content, title, destination, evidence=None):
    home = os.path.relpath(HERE / 'index.html', destination.parent)
    links = f'<a href="{html.escape(home, quote=True)}">Sample pack</a>'
    if evidence:
        links += ' · <a href="' + html.escape(evidence, quote=True) + '">Fictional evidence notes</a>'
    banner = (f'<aside style="padding:18px 24px;background:#fff1cc;border-bottom:3px solid #ae7b18;color:#44350e;font:15px/1.5 system-ui">'
              f'<strong>{html.escape(DISCLAIMER)}</strong><br>{html.escape(title)} · {links}</aside>')
    return content.replace('<body>', '<body>' + banner, 1)


def make_case(index, slug, status, cleanup):
    check_id = 'demo.single-draft-check'
    evidence = lambda section: 'evidence.html#' + section
    run = {'schema_version': '1.0', 'project_id': 'demo-' + slug, 'run_id': 'sample-' + slug,
        'stage': 'transactional-validation', 'environment': 'DEMO-TEST', 'started_at': '2026-10-20T10:00:00Z',
        'request': 'ILLUSTRATIVE: run one reviewed draft-transaction check in DEMO-TEST using existing references. Preview the exact action before execution.',
        'scope': 'One fictional draft transaction with one intrinsic line. No submission, approval workflow, downstream processing or wider implementation certification.',
        'scope_ref': evidence('scope'), 'requirement_version': 'DEMO-1.0', 'redaction_reviewed': True,
        'requirements': [], 'tasks': [], 'checks': [], 'decisions': [], 'recommendations': [], 'errors': [],
        'limitations': [DISCLAIMER,
            'Each example is an independent alternative with its own fictional project. The six cases are not a single project history or a batch execution.',
            'This is an output illustration, not an executable Oracle API, screen, privilege or cleanup specification. A real pillar must provide the reviewed supported route.',
            'Evidence is invented text in evidence.html. No real screenshot, API response, approval token or customer record is included.',
            'Only one primary record and one intrinsic line are in scope. A successful check does not verify the whole implementation.']}
    for n, (title, expected) in enumerate([
        ('Use an existing enabled business reference', 'DEMO-REFERENCE is enabled and retained on the draft.'),
        ('Save the intended one-line draft', 'One primary draft with one intrinsic line and quantity 1.')], 1):
        task = f'DEMO-T{n}'
        run['requirements'].append({'requirement_id': f'demo-r{n}', 'description': title,
            'source_ref': evidence('scope'), 'expected_setup': expected, 'task_refs': [task],
            'check_ids': [check_id], 'owner': 'Demo pillar SME (fictional)', 'required': True})
        run['tasks'].append({'task_id': task, 'title': 'Configure business reference' if n == 1 else 'Configure draft defaults',
            'status': 'completed', 'source_ref': evidence('tasks'), 'captured_at': '2026-10-20T09:50:00Z',
            'environment': 'DEMO-TEST', 'evidence_current': True,
            'details': 'Fictional task status only; correctness is assessed independently.',
            'owner': 'Demo implementer (fictional)', 'completed_at': f'2026-10-20T09:{10*n:02d}:00Z'})
    executed = status in ('PASS', 'FAIL', 'INDETERMINATE')
    observed = status in ('PASS', 'FAIL')
    record = f'DEMO-TXN-{index:03d}' if observed else ''
    check = {'result_id': 'demo-result-' + slug, 'check_id': check_id, 'check_version': 'DEMO-1.0',
        'title': 'Create and verify one draft transaction', 'owner': 'Demo pillar SME (fictional)',
        'required': True, 'blocking': True, 'requirement_refs': ['demo-r1', 'demo-r2'],
        'task_refs': ['DEMO-T1', 'DEMO-T2'], 'source_ref': evidence('procedure'), 'status': status,
        'method': 'manual-evidence' if executed else 'none', 'environment': 'DEMO-TEST',
        'observed_at': '2026-10-20T10:05:00Z', 'evidence_current': True, 'reason': '', 'assertions': [],
        'evidence_refs': [evidence('outcome')], 'performed_by': 'Demo implementer (fictional)' if executed else '',
        'next_action': '', 'transaction': {'test_key': 'DEMO-STABLE-' + slug.upper(), 'record_id': record,
            'request_id': '', 'new_primary_count': (None if status == 'INDETERMINATE' else 1 if observed else 0),
            'reused': False, 'approval_ref': evidence('execution-approval') if executed else '',
            'side_effects': [], 'cleanup_status': cleanup,
            'cleanup_evidence_refs': [evidence('cleanup')] if observed else [],
            'cleanup_owner': 'Demo implementer (fictional)', 'cleanup_next_action': ''}}
    expected = [('draft-created', 'One primary draft record exists with one intrinsic line.',
                 f'{record} is recorded as a draft with one intrinsic line.'),
                ('reference-retained', 'The draft retains the existing enabled DEMO-REFERENCE.',
                 f'{record} retains the enabled DEMO-REFERENCE.'),
                ('quantity-correct', 'The saved line quantity is 1.',
                 'The saved line quantity is 2.' if status == 'FAIL' else 'The saved line quantity is 1.')]
    for assertion_id, expectation, actual in expected:
        check['assertions'].append({'assertion_id': assertion_id, 'expected': expectation,
            'observed': actual if observed else '',
            'status': ('FAIL' if status == 'FAIL' and assertion_id == 'quantity-correct' else 'PASS') if observed else 'NOT_OBSERVED',
            'evidence_refs': [evidence('outcome')] if observed else []})
    if executed:
        run['decisions'].append({'decision_id': 'demo-execution-approval',
            'summary': 'Fictional approval at 10:01 UTC for the displayed one-record draft action in DEMO-TEST. This sample is not real authorization.',
            'owner': 'Demo project owner (fictional)', 'source_ref': evidence('execution-approval')})
    if status == 'PASS':
        check['reason'] = 'All three fictional observed business assertions match their stated expectations.'
    elif status == 'FAIL':
        check['reason'] = 'The saved quantity is 2, while the approved expectation is 1. Creation alone did not establish correctness.'
        check['next_action'] = 'Pillar SME: investigate the value mismatch and correct it through the approved implementation route; a later retest is a separate invocation.'
        run['recommendations'].append({'message': check['next_action'], 'owner': check['owner'], 'source_ref': evidence('outcome')})
    elif status == 'BLOCKED':
        check['reason'] = 'Pre-execution prerequisite review found DEMO-REFERENCE disabled. No save action was attempted.'
        check['next_action'] = 'Implementation owner: correct the reference through the implementation workflow and provide current evidence before requesting this check again.'
        run['tasks'][0]['details'] = 'Task is marked completed, but the prerequisite observation shows the reference disabled. Completion does not prove correctness.'
    elif status == 'SKIPPED':
        check['reason'] = 'The fictional project owner chose to skip this required check. No prerequisite review, creation or cleanup was performed for this invocation.'
        check['next_action'] = 'Project owner: accept the documented unverified scope or request this check later. Required route controls remain in force.'
        run['request'] = 'ILLUSTRATIVE: skip the offered transactional check for now and record its unverified scope.'
        run['decisions'].append({'decision_id': 'demo-user-skip', 'summary': check['reason'],
            'owner': 'Demo project owner (fictional)', 'source_ref': evidence('outcome')})
    else:
        check['reason'] = 'The fictional manual Save action timed out at 10:04 UTC. Subsequent confirmation was unavailable, so creation and stored values are unknown.'
        check['next_action'] = 'Reconcile the stable test key through the declared supported route. Do not retry Save or claim that zero records were created.'
        check['transaction']['cleanup_next_action'] = 'Identify whether a record exists before planning separately authorized exact-record cleanup.'
        run['errors'].append({'stage': 'transaction-save', 'failure_class': 'transport_or_environment',
            'message': 'DEMO-TEST; manual Save; illustrative elapsed wait 60 seconds; no confirmed record or server request ID; no repeat attempt.',
            'recommended_action': check['next_action'], 'artifact_refs': [evidence('outcome')], 'external_ids': []})
    tx = check['transaction']
    if observed:
        tx['side_effects'] = [f'One fictional primary draft {record} and one intrinsic line; no submission or downstream processing.',
                              'Fictional text evidence recorded at 10:05 UTC before any cleanup. No screenshot is included.']
        if cleanup == 'removed-verified':
            run['decisions'].append({'decision_id': 'demo-cleanup-approval',
                'summary': f'Fictional separate approval at 10:07 UTC for cleanup of {record} only, after evidence capture.',
                'owner': 'Demo project owner (fictional)', 'source_ref': evidence('cleanup')})
        else:
            tx['cleanup_next_action'] = f'Obtain separate approval for the supported cleanup of {record}; then verify its disposition. Owner: Demo implementer.'
            check['next_action'] = f'Coordinate with the Demo implementer to obtain separate cleanup approval for {record}, perform supported cleanup, and record verification.'
    elif status == 'INDETERMINATE':
        tx['side_effects'] = ['Primary record creation is unknown; no confirmed identity or cleanup outcome.']
    else:
        tx['side_effects'] = ['No transaction was attempted and no new record was created by this invocation.']
    run['checks'] = [check]
    return run


def evidence_html(run):
    c = run['checks'][0];tx = c['transaction']
    sections = {
        'scope': run['scope'] + ' Expectations are the two fictional requirement entries in the input JSON.',
        'procedure': 'Illustrative guided manual save and inspection. The real pillar must supply reviewed application steps, privileges and cleanup. No executable route is included in this sample.',
        'tasks': '\n'.join(f"{t['task_id']}: {t['status']}; source completion {t['completed_at']}; captured {t['captured_at']}. {t['details']}" for t in run['tasks']),
        'execution-approval': ('Fictional approval at 10:01 UTC for one exact draft action; no reusable token or real authorization.' if tx['approval_ref'] else 'No execution approval or attempted mutation is recorded.'),
        'outcome': c['reason'] + '\n' + '\n'.join(f"{a['assertion_id']}: expected {a['expected']} Observed: {a['observed'] or 'Not observed'}. Result {a['status']}." for a in c['assertions']),
        'cleanup': (f"Fictional observations captured 10:05 UTC; separate cleanup approval 10:07 UTC; removal of {tx['record_id']} 10:08 UTC; absence verified 10:09 UTC." if tx['cleanup_status'] == 'removed-verified' else
                    f"Disposition: {tx['cleanup_status']}. {tx['cleanup_next_action'] or 'No created record required cleanup in this invocation.'}")}
    body = f'<header><p class="eyebrow">FSCR · Fictional evidence catalog</p><h1>Evidence behind this example</h1><p>{html.escape(DISCLAIMER)}</p></header>'
    body += '<p><a href="transactional-validation.html">Return to report</a> · <a href="../../index.html">All samples</a></p>'
    for key, value in sections.items():
        body += f'<section id="{key}"><h2>{html.escape(key.replace("-", " ").title())}</h2><pre>{html.escape(value)}</pre></section>'
    return document('Fictional evidence — ' + run['project_id'], body)


def full_validation_overview(summary):
    """Show all three stages directly; counts and task rows come from assessed sources."""
    sources = {source['stage']: source for source in summary['sources']}
    stage_notes = {
        'prevalidation': (
            '1. Prevalidation', 'Environment and planned-scope readiness',
            'Seven checks passed. Run Book write verification was excluded because this assessment '
            'ran before Run Book creation. READY applies to that stage only; write access and setup correctness remain unproven.',
            'Open prevalidation report'),
        'implementation-review': (
            '2. Implementation review', 'Requirements, tasks and configured values',
            'At 10:00 UTC, the supplier site was inactive and approval-rule verification had not run. '
            'Two checks passed, one failed and one was not run. The report remains BLOCKED in history.',
            'Open implementation report'),
        'transactional-validation': (
            '3. Transactional validation', 'One draft transaction and its cleanup',
            'After prerequisite corrections were separately evidenced at 11:30 UTC, one manual draft-only check passed. '
            'One primary record was created; separately authorized cleanup was verified. This does not close the earlier implementation review.',
            'Open transaction report'),
    }
    cards = ''
    for stage, (title, purpose, explanation, link_label) in stage_notes.items():
        source = sources[stage]
        counts = source['counts']
        breakdown = ' · '.join(f'{value} {status}' for status, value in counts.items() if value)
        report_link = 'executive-story/' + source['report_ref']
        result_link = 'executive-story/' + source['result_ref']
        cards += (
            f'<article id="{stage}"><p class="eyebrow">{html.escape(purpose)}</p>'
            f'<h3>{title}</h3><span class="tag">{html.escape(source["outcome"])}</span>'
            f'<p><strong>{sum(counts.values())} recorded checks</strong><br>{html.escape(breakdown)}</p>'
            f'<p>{html.escape(explanation)}</p>'
            f'<p class="meta">Source run: {html.escape(source["recorded_at"])}</p>'
            f'<a class="button" href="{html.escape(report_link, quote=True)}">{link_label}</a>'
            f'<a href="{html.escape(result_link, quote=True)}">Result JSON</a></article>')
    task_rows = ''
    for snapshot in summary['tasks']:
        task = snapshot['task']
        completion = (task.get('completed_at') or 'Not recorded') if task['status'] == 'completed' else 'Not completed'
        values = (task['task_id'], task['title'], task['status'], completion, task['captured_at'])
        task_rows += '<tr>' + ''.join(f'<td>{html.escape(value)}</td>' for value in values) + '</tr>'
    metrics = ''.join(
        f'<div class="metric"><b>{summary["counts"][status]}</b><span>{label}</span></div>'
        for status, label in [('PASS', 'Passed results'), ('FAIL', 'Failed results'),
                              ('NOT_RUN', 'Not-run results'), ('NOT_APPLICABLE', 'Stage-excluded result')])
    evidence_index = 'executive-story/artifacts/shared/validation/demo-executive-summary/index.html'
    body = (
        '<header><p class="eyebrow">FSCR · Complete validation report · Synthetic review sample</p>'
        '<h1>Prevalidation, implementation<br>and transactional validation</h1>'
        '<p>Readiness passed within its stage. Implementation review found gaps. '
        'The later draft transaction passed after prerequisite corrections.</p>'
        f'<p>Project: {html.escape(summary["project_id"])} · Environment: {html.escape(summary["environment"])}</p></header>'
        f'<div class="notice"><strong>{DISCLAIMER}</strong><br>'
        'All three stages below belong to one fictional project history. Overall current project readiness has not been assessed.</div>'
        '<nav aria-label="Validation stage summaries"><a class="button" href="#prevalidation">Prevalidation</a>'
        '<a class="button" href="#implementation-review">Implementation review</a>'
        '<a class="button" href="#transactional-validation">Transactional validation</a></nav>'
        '<section><h2>Run Book tasks — latest supplied observations</h2>'
        '<p>All four task records are marked completed in the later supplied snapshot. '
        'These statuses do not prove that every configured value is correct or replace the earlier failed review.</p>'
        '<div class="scroll"><table><thead><tr><th>Task ID</th><th>Task</th><th>Recorded status</th>'
        '<th>Completed at — source time</th><th>Evidence captured</th></tr></thead>'
        f'<tbody>{task_rows}</tbody></table></div>'
        '<p class="meta">Times include their source timezone; Z means UTC. '
        'Rows come from the supplied transaction-prerequisite snapshot, not a new live Run Book read.</p></section>'
        f'<section><h2>Executive summary — all three validation stages</h2>'
        f'<p><strong>{len(summary["sources"])} stage reports · {summary["recorded_check_results"]} recorded check results'
        f' · {len(summary["tasks"])} distinct supplied Run Book tasks</strong></p>'
        f'<div class="metrics">{metrics}</div>'
        '<p class="meta">These are historical check-result counts, not a project success percentage. '
        'A BLOCKED implementation-stage outcome can result from a failed check; it does not require a separate BLOCKED check row. '
        'No recorded checks are INDETERMINATE or SKIPPED in this particular three-stage story.</p>'
        f'<div class="cards stage-cards">{cards}</div></section>'
        '<section><h2>How the outcomes fit together</h2><div class="scroll"><table>'
        '<thead><tr><th>Time — UTC</th><th>Recorded event</th><th>What it means</th></tr></thead><tbody>'
        '<tr><td>08:00</td><td>Prevalidation: READY in pre_runbook scope</td><td>Seven prerequisite checks passed; write verification was excluded by stage.</td></tr>'
        '<tr><td>10:00</td><td>Implementation review: BLOCKED</td><td>Supplier/site mismatch and an unrun approval-rule check remain in this report.</td></tr>'
        '<tr><td>11:30</td><td>Later prerequisite correction evidence reviewed</td><td>The selected transaction’s needed corrections were evidenced before it ran. This is not a new full implementation review.</td></tr>'
        '<tr><td>12:00–12:09</td><td>One draft transaction passed; cleanup verified</td><td>The narrow draft scenario passed. Evidence preceded separate cleanup approval and removal.</td></tr>'
        '</tbody></table></div>'
        '<p><strong>Next action:</strong> request a fresh implementation review against current evidence if a current implementation-readiness decision is needed. '
        'Keep the original gaps and their history visible.</p>'
        f'<a class="button" href="{evidence_index}">Open full evidence index</a></section>'
        '<section><h2>Additional transaction outcome examples</h2>'
        '<p>Six independent alternatives demonstrate successful cleanup, pending cleanup, blocked execution, '
        'failed business assertions, a user skip and an unknown creation outcome. They are separate from the project history above.</p>'
        '<a class="button" href="transaction-examples.html">Browse the six transaction examples</a>'
        '<p><a href="README.md">Sharing and developer notes</a> · '
        '<a href="sample-conversations.md">Example conversations</a> · '
        '<a href="manifest.json">File manifest and checksums</a></p></section>'
        '<footer>All observations, identities and approvals are fictional. '
        'Reports use the updated framework assessment/rendering helpers. No live operations were performed.</footer>')
    content = document('FSCR — prevalidation, implementation and transactional validation summary', body)
    return content.replace('</style>', '.stage-cards{grid-template-columns:repeat(3,minmax(0,1fr))}'
                           '@media(max-width:960px){.stage-cards{grid-template-columns:1fr}}</style>', 1)


def build(renderer_root, dry_run):
    sys.path.insert(0, str(renderer_root / 'core/validation/reporting/scripts'))
    import validation_report as report
    import executive_summary as executive
    rendered = {}
    results = []
    for n, (slug, title, status, cleanup, readiness, description) in enumerate(CASES, 1):
        data = make_case(n, slug, status, cleanup)
        assessment = report.assess(data)
        assert assessment['readiness'] == readiness, (slug, assessment)
        folder = HERE / 'cases' / slug
        target = folder / 'transactional-validation.html'
        rendered[target] = badge(report.render(data, assessment), title + ' · Independent alternative', target, 'evidence.html')
        rendered[folder/'transactional-validation.input.json'] = dump(data)
        rendered[folder/'transactional-validation.json'] = dump({'run': data, 'assessment': assessment})
        rendered[folder/'evidence.html'] = evidence_html(data)
        results.append({'slug': slug, 'title': title, 'status': status, 'cleanup': cleanup, 'readiness': readiness,
                        'description': description, 'new_primary_count': data['checks'][0]['transaction']['new_primary_count']})
    # Separate historical story: build real source pairs in an ephemeral test workspace,
    # then copy only report artifacts to the share pack. No project is initialized in FSCR.
    with tempfile.TemporaryDirectory(prefix='fscr-output-samples-') as temporary:
        root = Path(temporary)
        project_id = 'demo-procurement-validation'
        project = root / 'project' / project_id
        (project/'state').mkdir(parents=True)
        (project/'state/project-state.json').write_text(dump({'project_id': project_id}))
        entries = []
        for stage in ('prevalidation', 'implementation-review', 'transactional-validation'):
            data = report.load(HERE/'fixtures'/(stage+'.input.json'))
            relative = Path('artifacts/shared/validation') / data['run_id']
            stem = 'readiness' if stage == 'prevalidation' else stage
            source_json = relative / (stem+'.json'); source_html = relative / (stem+'.html')
            destination = HERE/'executive-story'/source_html
            if stage == 'prevalidation':
                content = executive.prevalidation.render(data); payload = data
            else:
                assessment = report.assess(data)
                content = report.render(data, assessment);payload = {'run': data, 'assessment': assessment}
            rendered[destination] = badge(content, 'Three-stage fictional project history', destination, 'sample-evidence.html')
            rendered[HERE/'executive-story'/source_json] = dump(payload)
            evidence_destination = destination.parent/'sample-evidence.html'
            evidence_home = os.path.relpath(HERE/'index.html', evidence_destination.parent)
            rendered[evidence_destination] = (HERE/'fixtures/story-evidence.html').read_text().replace('href="../index.html"', f'href="{evidence_home}"')
            for rel in (source_json,source_html):
                path=project/rel;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(rendered[HERE/'executive-story'/rel])
            entries.append({'kind': 'prevalidation' if stage=='prevalidation' else 'validation',
                'result_ref': str(source_json), 'result_sha256': hashlib.sha256((project/source_json).read_bytes()).hexdigest(),
                'report_ref': str(source_html), 'report_sha256': hashlib.sha256((project/source_html).read_bytes()).hexdigest()})
        manifest = {'schema_version':'1.0','project_id':project_id,'summary_id':'demo-executive-summary',
            'generated_at':'2026-10-20T14:00:00Z','environment':'DEMO-TEST','environment_url':'https://demo-test.example.invalid',
            'redaction_reviewed':True,'sources':entries}
        collected = executive.collect(manifest,root)
        assert collected['recorded_check_results']==13 and collected['counts']['PASS']==10
        assert collected['counts']['FAIL']==1 and collected['counts']['NOT_RUN']==1 and collected['counts']['NOT_APPLICABLE']==1
        directory=HERE/'executive-story/artifacts/shared/validation/demo-executive-summary'
        rendered[directory/'index.html']=badge(executive.render(collected),'Three-stage fictional project history',directory/'index.html')
        rendered[directory/'index.json']=dump(collected)
        rendered[HERE/'executive-story/summary-manifest.json']=dump(manifest)
    counts=Counter(item['status'] for item in results)
    cards=''
    for n,item in enumerate(results,1):
        base='cases/'+item['slug']+'/'
        value='Unknown' if item['new_primary_count'] is None else str(item['new_primary_count'])
        cards += (f'<article><span class="tag">Example {n:02d} · {item["status"]}</span><h3>{item["title"]}</h3>'
            f'<p>{item["description"]}</p><p><b>Readiness:</b> <code>{item["readiness"]}</code><br>'
            f'<b>New primary records:</b> {value}<br><b>Cleanup:</b> {item["cleanup"]}</p>'
            f'<a class="button" href="{base}transactional-validation.html">View report</a>'
            f'<a href="{base}transactional-validation.json">Result JSON</a> · <a href="{base}evidence.html">Evidence notes</a></article>')
    story='executive-story/artifacts/shared/validation/demo-executive-summary/index.html'
    body=(f'<header><p class="eyebrow">FSCR · Pillar developer review pack · 20 October 2026</p><h1>Transactional validation<br>Sample outputs</h1>'
        '<p>See what an implementer receives after one selected check: task status, business assertions, evidence, owners, next actions and cleanup.</p></header>'
        f'<div class="notice"><strong>{DISCLAIMER}</strong><br>These are report examples, not executable pillar checks or customer validation results.</div>'
        '<div class="metrics"><div class="metric"><b>6</b><span>Independent transaction examples</span></div>'
        f'<div class="metric"><b>{counts["PASS"]}</b><span>Examples with passing business checks</span></div>'
        '<div class="metric"><b>1</b><span>Separate executive-summary example</span></div>'
        '<div class="metric"><b>0</b><span>Real transactions executed</span></div></div>'
        '<section><h2>Start with the final project report</h2><p>A separate fictional history shows prevalidation, an implementation review with gaps, and a later successful single transaction. Its calculated summary contains <strong>3 reports / 13 recorded results: 10 PASS, 1 FAIL, 1 NOT_RUN and 1 NOT_APPLICABLE</strong>. The earlier implementation failure stays visible.</p>'
        f'<a class="button" href="{story}">Open executive summary</a><p class="meta">This history is separate from the six alternative cases below. The six cases are never counted as one project or batch run.</p></section>'
        '<section><h2>Choose a transactional outcome</h2><p>Each example has two fictional Run Book tasks at the top and one selected check. Completion of those tasks does not determine the business result.</p>'
        f'<div class="cards">{cards}</div></section>'
        '<section><h2>What to review with your team</h2><div class="scroll"><table><tr><th>Question</th><th>What the output should make clear</th></tr>'
        '<tr><td>Was the transaction actually verified?</td><td>Expected versus observed assertions, evidence and performer are distinct from task status.</td></tr>'
        '<tr><td>What is still unresolved?</td><td>Failure, missing prerequisites, skip decisions and uncertain creation stay visible with an owner and next action.</td></tr>'
        '<tr><td>What happened to test data?</td><td>Cleanup has its own disposition and evidence. A passing transaction can still need review.</td></tr>'
        '<tr><td>Can the developer reuse the format?</td><td>Each case includes the sanitized run input and the assessed result JSON; HTML uses the updated framework renderer.</td></tr></table></div>'
        '<p><a href="README.md">Sharing and developer notes</a> · <a href="sample-conversations.md">Example user conversations</a> · <a href="manifest.json">File manifest and checksums</a></p></section>'
        '<footer>Offline HTML and JSON · All names, timestamps, observations and approvals are fictional · No scripts or external assets</footer>')
    body = '<p><a class="button" href="index.html">Return to the complete three-stage validation summary</a></p>' + body
    rendered[HERE/'transaction-examples.html']=document('FSCR transactional validation — additional examples',body)
    rendered[HERE/'index.html']=full_validation_overview(collected)
    rendered[HERE/'README.md']=readme(results)
    rendered[HERE/'sample-conversations.md']=conversations(results)
    if dry_run:
        print(dump({'mode':'dry-run','independent_cases':len(results),'validated_story_reports':3,
                    'story_result_count':collected['recorded_check_results'],'planned_generated_files':len(rendered)}))
        return
    for path, content in rendered.items():
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding='utf-8')
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.name!='manifest.json':
            files.append({'path':str(path.relative_to(HERE)),'bytes':path.stat().st_size,
                          'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (HERE/'manifest.json').write_text(dump({'sample_only':True,'no_live_execution':True,'date':'2026-10-20',
        'cases':results,'story_check_counts':collected['counts'],'files':files,
        'renderer_sources':{str(p.relative_to(renderer_root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            renderer_root/'core/validation/reporting/scripts/validation_report.py',
            renderer_root/'core/validation/reporting/scripts/executive_summary.py',
            renderer_root/'shared/validation/prevalidation/scripts/render_readiness_report.py']}}))
    archive=HERE.parent/'fscr-validation-complete-sample-reports-20261020.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED) as zip_file:
        for path in sorted(HERE.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                zip_file.write(path,Path(HERE.name)/path.relative_to(HERE))
    # Keep the previously shared download current as well.
    shutil.copy2(archive, HERE.parent/(HERE.name+'.zip'))
    print(dump({'landing_page':str(HERE/'index.html'),'archive':str(archive),'files':len(files)+1}))


def readme(results):
    text='''# FSCR complete validation — sample output pack

**Synthetic review material. No Fusion system was accessed; no real transaction, approval or cleanup occurred.**

Unzip the full folder and open `index.html` in a browser. Share the ZIP to preserve all report links. The HTML is self-contained, script-free and uses no external assets. It can be printed from a browser. JSON and Markdown can be read in any text editor.

## Start with all three stages

The main `index.html` directly displays the Run Book tasks, calculated executive counts and three clearly labeled stage summaries:

| Stage | Recorded outcome | Check results |
| --- | --- | --- |
| Prevalidation | READY before Run Book creation; write access remains unverified | 7 PASS, 1 NOT_APPLICABLE |
| Implementation review | BLOCKED at the original review | 2 PASS, 1 FAIL, 1 NOT_RUN |
| Transactional validation | READY_WITHIN_VERIFIED_SCOPE for one later draft check; cleanup verified | 1 PASS |

Each stage has a direct link to its detailed HTML report and JSON. These are one coherent fictional history: 3 reports and 13 recorded results. Later prerequisite corrections permit the selected transaction; they do not turn the original implementation review into PASS. No newer full implementation review is included, and overall current project readiness is not assessed.

## Additional independent transaction examples

Open `transaction-examples.html` for the six alternative outcomes below.

The six transaction cases are independent alternatives, each with a separate fictional project. They are not a batch execution or a sequence of successful/failed attempts in one project. Each contains exactly one selected check and at most one known new primary transaction; an uncertain outcome retains a null count.

| Example | Check result | Readiness | Cleanup |
| --- | --- | --- | --- |
'''
    for item in results:
        text+=f'| [{item["title"]}](cases/{item["slug"]}/transactional-validation.html) | {item["status"]} | {item["readiness"]} | {item["cleanup"]} |\n'
    return text+'''
The `executive-story/` files back the main three-stage dashboard and the full evidence index. Do not combine their counts with the independent transaction examples.

## Files in each case

- `transactional-validation.html`: user-facing report from the updated framework renderer, with an added sample banner/navigation.
- `transactional-validation.input.json`: fictional sanitized run envelope supplied to the renderer.
- `transactional-validation.json`: the run and its calculated assessment.
- `evidence.html`: matching fictional observation, decision and cleanup notes. No real screenshots or server responses are included.

`executive-story/` contains the separate report hierarchy and source manifest. Its relative paths match the production index layout. These sample files are not a registered/live implementation project: no real project-state update, artifact-registry publication or execution audit is claimed.

## Responsibilities

Pillars define the bounded scenario, prerequisites, supported API or reviewed manual route, business assertions and cleanup. The framework coordinates selection and controls, validates the result envelope, and generates common reports. A real execution route, current product documentation and required permissions must be supplied separately; none is implied by these examples.

One transaction may have several assertions. A completed Run Book task, successful request or successful cleanup cannot manufacture a passing business assertion. User skips remain unverified; timeout outcomes must be reconciled before another create attempt. Keep sensitive payloads/session objects out of report artifacts.

## Rebuild

From a checkout containing the updated validation reporting helpers:

```sh
python3 build_samples.py --renderer-root /path/to/validation-framework-checkout --dry-run
python3 build_samples.py --renderer-root /path/to/validation-framework-checkout
```

This builder uses pure local assessment/rendering functions and an ephemeral synthetic context. It never contacts Fusion or runs pillar tests. The source fixture story is included under `fixtures/`. `manifest.json` records package checksums and renderer source hashes for review; hashes cover report/code files only, not Data Loader payloads.
'''


def conversations(results):
    text='''# Illustrative user-visible conversations

All dialogue below is fictional. In a real run, the exact environment, supported operation and payload must be shown before required authorization. These abbreviations are not executable approval prompts.

'''
    responses = [
        'The selected check passed. One draft was created, its expected values matched, and separately authorized cleanup was verified. Readiness is READY_WITHIN_VERIFIED_SCOPE for this one check. Wider implementation readiness is not established.',
        'The business assertions passed, but cleanup has not been completed. Readiness is NEEDS_REVIEW. The report names the cleanup owner and required next action; it does not claim that the record was removed.',
        'The prerequisite reference is disabled, so this check is BLOCKED. No transaction was attempted. The implementation owner must correct the prerequisite and provide current evidence before a later request.',
        'One record was created, but the observed quantity was 2 instead of the expected 1. The check is FAIL and readiness is BLOCKED. Cleanup was separately verified; that does not change the failed business assertion.',
        'I recorded your decision as SKIPPED. No transaction was attempted, and the selected requirement remains unverified. Readiness is NEEDS_REVIEW. Skipping does not waive controls for future execution.',
        'The save timed out and the outcome is INDETERMINATE. The created-record count is unknown, not zero. Reconcile the stable test key through the declared route before another attempt. Cleanup is also unknown.'
    ]
    for item,response in zip(results,responses):
        prompt='Skip the offered transactional check for now and record that decision.' if item['status']=='SKIPPED' else 'Run the reviewed single-draft transactional check for this project in DEMO-TEST.'
        text+=f'## {item["title"]}\n\n**Human:** “{prompt}”\n\n**Final response after the fictional outcome:** “{response}”\n\n[Open the sample report](cases/{item["slug"]}/transactional-validation.html).\n\n'
    return text.rstrip() + '\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer-root',type=Path,required=True,help='Checkout containing the updated core validation reporting helpers')
    parser.add_argument('--dry-run',action='store_true',help='Validate and render in memory; do not write sample outputs')
    args=parser.parse_args()
    build(args.renderer_root.resolve(),args.dry_run)
