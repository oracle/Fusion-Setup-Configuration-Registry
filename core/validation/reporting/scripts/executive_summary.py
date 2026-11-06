#!/usr/bin/env python3
"""Build a local project index from explicit, immutable validation report sources."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import html
import importlib.util
from pathlib import Path
import re
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validation_report as report

spec = importlib.util.spec_from_file_location('prevalidation_report',
    report.ROOT / 'shared/validation/prevalidation/scripts/render_readiness_report.py')
prevalidation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prevalidation)
STATUSES = ('PASS', 'FAIL', 'BLOCKED', 'REVIEW_NEEDED', 'INDETERMINATE', 'SKIPPED', 'NOT_RUN', 'NOT_APPLICABLE')
ID = re.compile(r'^[a-z0-9][a-z0-9._-]{0,119}$')
DIGEST = re.compile(r'^[a-f0-9]{64}$')


def timestamp(value):
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError()
        return stamp
    except (ValueError, TypeError, AttributeError):
        raise report.InputError('summary/source timestamp must include a timezone') from None


def fields(value, required):
    if not isinstance(value, dict) or set(value) != set(required):
        raise report.InputError('summary manifest/source has missing or unsupported fields')


def source_file(project, relative, digest, suffix):
    if (not isinstance(relative, str) or not relative.startswith('artifacts/shared/validation/')
            or Path(relative).is_absolute() or any(p in ('.', '..') for p in relative.split('/'))
            or '\\' in relative or ':' in relative or '#' in relative or '?' in relative
            or Path(relative).suffix != suffix):
        raise report.InputError('source must be a project-relative validation artifact path')
    if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
        raise report.InputError('source checksum must be a SHA-256 digest')
    path = report.safe_target(project, relative)
    if not path.is_file():
        raise report.InputError('source is missing')
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise report.InputError('source is missing or changed; review it and refresh the manifest')
    return path, content


def collect(manifest, root=report.ROOT):
    """Recalculate history; never turn a stage outcome into overall project success."""
    fields(manifest, ('schema_version', 'project_id', 'summary_id', 'generated_at', 'environment',
                      'environment_url', 'redaction_reviewed', 'sources'))
    if manifest['schema_version'] != '1.0' or manifest['redaction_reviewed'] is not True:
        raise report.InputError('summary requires version 1.0 and reviewed, sanitized sources')
    for key in ('project_id', 'summary_id'):
        if not isinstance(manifest[key], str) or not ID.fullmatch(manifest[key]):
            raise report.InputError('project_id/summary_id must be safe lowercase identifiers')
    for key in ('environment', 'environment_url'):
        if not isinstance(manifest[key], str) or not manifest[key].strip():
            raise report.InputError('summary requires an environment name and base URL')
    # Use the same origin rules as prevalidation, even for summaries without that stage.
    from urllib.parse import urlsplit
    origin = urlsplit(manifest['environment_url'])
    if (origin.scheme != 'https' or not origin.hostname or origin.username or origin.password
            or origin.query or origin.fragment or origin.path not in ('', '/')):
        raise report.InputError('environment_url must be a credential-free HTTPS base origin')
    generated = timestamp(manifest['generated_at'])
    if not isinstance(manifest['sources'], list) or not manifest['sources']:
        raise report.InputError('summary needs at least one explicit source report')
    project = report.safe_project(root, manifest['project_id'])
    state = report.load(report.safe_target(project, 'state/project-state.json'))
    if not isinstance(state, dict) or state.get('project_id') != manifest['project_id']:
        raise report.InputError('project identity mismatch')
    sources, findings, tasks = [], [], {}
    counts = Counter({status: 0 for status in STATUSES})
    used_paths, used_runs, baselines = set(), set(), set()
    cleanup = Counter()
    created_known, created_unknown, reuse_runs = 0, 0, 0
    for entry in manifest['sources']:
        fields(entry, ('kind', 'result_ref', 'result_sha256', 'report_ref', 'report_sha256'))
        if entry['kind'] not in ('prevalidation', 'validation'):
            raise report.InputError('unsupported summary source kind')
        result_path, result_bytes = source_file(project, entry['result_ref'], entry['result_sha256'], '.json')
        source_file(project, entry['report_ref'], entry['report_sha256'], '.html')
        # Both published files must be the pair from the same run directory.
        if Path(entry['result_ref']).with_suffix('.html') != Path(entry['report_ref']):
            raise report.InputError('source JSON and HTML must be a matching report pair')
        if entry['result_ref'] in used_paths:
            raise report.InputError('duplicate source would double-count results')
        used_paths.add(entry['result_ref'])
        payload = report.loads(result_bytes.decode("utf-8"))
        if entry['kind'] == 'prevalidation':
            try:
                outcome = prevalidation.validate_report(payload)
            except (ValueError, TypeError, KeyError) as error:
                raise report.InputError('invalid prevalidation source') from error
            if (payload['target_environment']['name'] != manifest['environment']
                    or payload['target_environment']['base_url'].rstrip('/') != manifest['environment_url'].rstrip('/')):
                raise report.InputError('prevalidation environment differs from summary')
            if payload.get('project_id', manifest['project_id']) != manifest['project_id']:
                raise report.InputError('prevalidation project differs from summary')
            run_id, observed = payload['run_id'], payload['generated_at']
            stage = 'prevalidation'
            scope = report.dump(payload['selected_scope']).strip()
            baseline = 'Environment readiness; requirement baseline not recorded in this source'
            stage_scope = payload.get('assessment_stage', 'full_readiness')
            local_counts = Counter(prevalidation.check_status(c).replace(' ', '_') for c in payload['checks'])
            for check in payload['checks']:
                if prevalidation.check_status(check) == 'REVIEW NEEDED':
                    findings.append({'run_id': run_id, 'stage': stage, 'status': prevalidation.check_status(check),
                        'title': check.get('implementation_message', check['check_name']), 'owner': 'Not recorded — assign an owner',
                        'expected': 'Required prerequisite' if check['required'] else 'Advisory readiness check',
                        'observed': check['live_environment_evidence'], 'evidence': check['artifact_references'],
                        'next_action': check['recommended_remediation'], 'observed_at': observed})
            for category in prevalidation.report_categories(payload):
                if not any(c['category'] == category and c['required'] for c in payload['checks']):
                    findings.append({'run_id': run_id, 'stage': stage, 'status': 'REVIEW NEEDED',
                        'title': 'Missing required category: ' + category, 'owner': 'Framework coordinator',
                        'expected': 'Recorded required assessment', 'observed': 'Not recorded', 'evidence': [],
                        'next_action': 'Complete the supported assessment or disclose the blocker.', 'observed_at': observed})
        else:
            fields(payload, ('run', 'assessment'))
            data = payload['run']
            assessment = report.assess(data)
            if assessment != payload['assessment']:
                raise report.InputError('stored assessment differs from recomputed result; regenerate the source report')
            if data['project_id'] != manifest['project_id'] or data['environment'] != manifest['environment']:
                raise report.InputError('validation project/environment differs from summary')
            run_id, observed, stage = data['run_id'], data['started_at'], data['stage']
            outcome, scope, stage_scope = assessment['readiness'], data['scope'], assessment['readiness_scope']
            baseline = data['requirement_version'] + ' / ' + data['scope_ref']
            baselines.add(data['requirement_version'])
            local_counts = Counter(assessment['counts'])
            for task in data['tasks']:
                captured = timestamp(task['captured_at'])
                if task['status'] == 'completed' and task.get('completed_at') and timestamp(task['completed_at']) > captured:
                    raise report.InputError('task completion time is later than its capture time')
                if captured > generated:
                    raise report.InputError('task evidence is later than the summary timestamp')
                old = tasks.get(task['task_id'])
                if old and captured == timestamp(old['captured_at']) and task != old['task']:
                    raise report.InputError('conflicting task snapshots at the same capture time')
                if old is None or captured > timestamp(old['captured_at']):
                    tasks[task['task_id']] = {'task': task, 'captured_at': task['captured_at'], 'run_id': run_id}
            for check in data['checks']:
                if timestamp(check['observed_at']) > generated:
                    raise report.InputError('check evidence is later than the summary timestamp')
                if check['status'] not in ('PASS', 'NOT_APPLICABLE') or not check['evidence_current']:
                    findings.append({'run_id': run_id, 'stage': stage, 'status': check['status'],
                        'title': check['title'], 'owner': check['owner'],
                        'expected': [a['expected'] for a in check['assertions']],
                        'observed': [a['observed'] for a in check['assertions']] or check['reason'],
                        'evidence': check['evidence_refs'], 'next_action': check['next_action'] or 'Review the recorded gap.',
                        'observed_at': check['observed_at']})
                if 'transaction' in check:
                    tx = check['transaction']
                    count = tx['new_primary_count']
                    if count is None:
                        created_unknown += 1
                    else:
                        created_known += count
                    reuse_runs += int(tx['reused'])
                    cleanup[tx['cleanup_status']] += 1
            for message in assessment['gaps'] + assessment['blockers']:
                findings.append({'run_id': run_id, 'stage': stage, 'status': 'REVIEW', 'title': message,
                    'owner': 'Project owner / relevant check owner', 'expected': 'Complete verified coverage',
                    'observed': 'See source report', 'evidence': [entry['result_ref']],
                    'next_action': 'Review the source report and assign the follow-up.', 'observed_at': observed})
        if timestamp(observed) > generated:
            raise report.InputError('source report is later than summary timestamp')
        if run_id in used_runs:
            raise report.InputError('duplicate run identity in summary')
        used_runs.add(run_id)
        counts.update(local_counts)
        sources.append({**entry, 'run_id': run_id, 'stage': stage, 'recorded_at': observed,
                        'outcome': outcome, 'scope': scope, 'stage_scope': stage_scope,
                        'baseline': baseline, 'counts': {s: local_counts[s] for s in STATUSES}})
    if len(baselines) > 1:
        raise report.InputError('different requirement baselines need separate summaries')
    sources.sort(key=lambda s: (timestamp(s['recorded_at']), s['run_id']))
    tasks = [tasks[k] for k in sorted(tasks)]
    return {'schema_version': '1.0', 'project_id': manifest['project_id'], 'summary_id': manifest['summary_id'],
            'generated_at': manifest['generated_at'], 'environment': manifest['environment'],
            'environment_url': manifest['environment_url'], 'summary_type': 'historical_evidence_index',
            'project_readiness': 'NOT_ASSESSED', 'sources': sources, 'counts': dict(counts),
            'recorded_check_results': sum(counts.values()), 'tasks': tasks, 'findings': findings,
            'transaction_counts': {'known_created_records_across_runs': created_known,
                'runs_with_unknown_created_count': created_unknown, 'runs_reusing_records': reuse_runs,
                'cleanup_dispositions': dict(cleanup)}}


def esc(value):
    return html.escape(report.dump(value).strip() if isinstance(value, (list, dict)) else str(value), quote=True)


def table(headers, rows):
    return ('<table><thead><tr>' + ''.join('<th>' + esc(h) + '</th>' for h in headers) +
            '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + esc(c) + '</td>' for c in row) +
            '</tr>' for row in rows) + '</tbody></table>')


def render(summary):
    cards = ''.join(f'<div class="metric"><strong>{summary["counts"][s]}</strong><span>{s}</span></div>' for s in STATUSES)
    tasks = []
    for snapshot in summary['tasks']:
        task = snapshot['task']
        completed = (task.get('completed_at') or 'Not recorded') if task['status'] == 'completed' else ('Not applicable' if task['status'] == 'not-applicable' else 'Not completed')
        tasks.append((task['task_id'], task['title'], task['status'], completed,
                      task['captured_at'], snapshot['run_id'], 'Current' if task['evidence_current'] else 'Stale'))
    task_table = table(['Task', 'Title', 'Recorded status', 'Source completion time', 'Captured at', 'Source run', 'Evidence'], tasks) if tasks else '<p>No execution task snapshots recorded. Planned prevalidation tasks are not completed tasks.</p>'
    stages = ''
    for source in summary['sources']:
        # Target is generated solely from a validated project-relative artifact path.
        link = quote('../../../../' + source['report_ref'], safe='/')
        stages += (f'<article><p class="eyebrow">{esc(source["stage"])}</p><h3>{esc(source["outcome"])}</h3>'
            f'<p>{esc(source["run_id"])} · {esc(source["recorded_at"])}</p>'
            f'<p><strong>Scope:</strong> {esc(source["scope"])}</p><p>{esc(source["stage_scope"])}</p>'
            f'<p><strong>Baseline:</strong> {esc(source["baseline"])}</p>'
            f'<p>{esc(source["counts"])}</p><a href="{link}">Open stage report</a></article>')
    findings = ''
    for item in summary['findings']:
        findings += (f'<article><h3>{esc(item["status"])} · {esc(item["title"])}</h3>'
            + table(['Field', 'Recorded value'], [(k.replace('_', ' ').title(), v) for k, v in item.items() if k not in ('title', 'status')]) + '</article>')
    stages_present = {s['stage'] for s in summary['sources']}
    missing = [s for s in ('prevalidation', 'implementation-review', 'transactional-validation') if s not in stages_present]
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
        '<title>FSCR validation executive summary</title><style>'
        'body{font:16px/1.55 system-ui,sans-serif;margin:0;background:#f3f2ed;color:#25332f}main{max-width:1280px;margin:auto;padding:32px}'
        'header{background:#153f36;color:white;padding:32px;border-radius:12px}h1{font-size:36px;margin:8px 0}h2{font-size:24px;margin-top:0}'
        'section{background:white;border:1px solid #d9dfd8;border-radius:10px;padding:24px;margin-top:24px}.metrics,.stages{display:flex;flex-wrap:wrap;gap:14px}'
        '.metric{background:#f0f4ef;padding:16px;flex:1;min-width:100px}.metric strong{display:block;font-size:34px}.metric span,.eyebrow{font-size:12px;letter-spacing:1px}'
        'article{padding:20px;border:1px solid #d9dfd8;border-radius:8px;margin-top:16px;overflow-wrap:anywhere}.stages article{flex:1;min-width:260px}'
        'table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;padding:10px;border:1px solid #d9dfd8;overflow-wrap:anywhere;white-space:pre-wrap}'
        'th{background:#eef2ed}a{color:#1b6455}.scroll{overflow-x:auto}.note{color:#52645a}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
        '@media(max-width:720px){main{padding:12px}header,section{padding:16px}h1{font-size:28px}table{min-width:680px}}'
        '@media print{body{background:white}main{padding:0}header{color:#153f36;background:white}article{break-inside:avoid}table{font-size:10px;min-width:0}}'
        '</style></head><body><main>'
        f'<header><p class="eyebrow">FSCR · VALIDATION EXECUTIVE SUMMARY</p><h1>Evidence at a glance</h1>'
        f'<p>{esc(summary["project_id"])} · {esc(summary["environment"])} · {esc(summary["generated_at"])}</p>'
        '<p>Historical evidence index. Overall project readiness is not assessed by this summary.</p></header>'
        '<section><h2>Run Book tasks</h2><p>Latest supplied observation per task, selected by capture time. This may combine runs; it is not a live complete Run Book snapshot. Completion time comes from the source.</p>'
        f'<div class="scroll">{task_table}</div></section>'
        f'<section><h2>Executive summary</h2><p><strong>{len(summary["sources"])} reports · {summary["recorded_check_results"]} recorded check results · {len(summary["tasks"])} distinct observed tasks</strong></p>'
        f'<div class="metrics">{cards}</div><p class="note">Counts include every selected historical result, including repeat checks. They are not unique capability counts or a project success percentage. Missing evidence never becomes PASS.</p>'
        f'<p><strong>Stages without supplied reports:</strong> {esc(", ".join(missing) or "None")}. A missing report does not prove a stage ran or was skipped.</p></section>'
        f'<section><h2>Stage outcomes and report links</h2><div class="stages">{stages}</div></section>'
        '<section><h2>Findings and next actions</h2><p>Historical findings remain visible. A later passing transaction does not close an earlier implementation gap. Reassess the affected requirement and reference the resulting decision. Entries may describe the same underlying issue; they are not an issue-count metric.</p>'
        + (findings or '<p>No findings recorded in these sources. Review each source’s scope and limitations before deciding whether further validation is needed.</p>') + '</section>'
        '<section><h2>Transaction records and cleanup</h2><p>These are per-run observations, not a count of unique or currently retained Fusion records. A zero known-created count with unknown-count runs does not mean no records were created. Scenario success and cleanup are separate.</p>'
        + table(['Metric', 'Value'], list(summary['transaction_counts'].items())) + '</section>'
        '<section><h2>Evidence boundaries</h2><p>This local summary recalculates existing report assessments and checks source hashes; it makes no Fusion calls. It cannot establish that submitted evidence is truthful or still current. Environment labels on implementation/transaction sources must already be bound to the selected environment by the routed workflow. Prevalidation scope remains separate from requirement coverage.</p>'
        '<p>Source versions and checksums, task provenance, and individual historical outcomes are preserved in index.json. Read the stage reports for assertions, manual attribution, limitations, approvals and cleanup evidence.</p></section></main></body></html>\n')


def publish(manifest, root=report.ROOT):
    # Re-read and re-hash immediately before generating the immutable output bundle.
    summary = collect(manifest, root)
    return report.publish_bundle(project_id=manifest['project_id'], run_id=manifest['summary_id'],
        started_at=manifest['generated_at'], bodies={'index.html': render(summary), 'index.json': report.dump(summary)},
        input_refs=[s['result_ref'] for s in manifest['sources']],
        notes='Historical validation summary generated; overall project readiness NOT_ASSESSED.',
        input_tokens=max(1, len(report.dump(manifest) + report.dump(summary)) // 4),
        files_read=1 + 2 * len(manifest['sources']), root=root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Sanitized summary manifest JSON')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true', help='Validate explicit source files and compute metrics without writes')
    mode.add_argument('--publish', action='store_true', help='Publish a new append-only project index.html/index.json')
    args = parser.parse_args()
    try:
        manifest = report.load(args.input)
        if args.dry_run:
            summary = collect(manifest)
            result = {'mode': 'dry-run', 'report_count': len(summary['sources']), 'counts': summary['counts'],
                      'project_readiness': summary['project_readiness']}
        else:
            result = publish(manifest)
        print(report.dump(result))
        return 0  # Successful indexing is never a business readiness decision.
    except (report.InputError, ValueError, TypeError, KeyError):
        print(report.dump({'status': 'failed', 'failure_class': 'input_validation',
            'message': 'Invalid summary input, identity, source contract, checksum, or scope. No Fusion call was made.',
            'recommended_action': 'Review the summary manifest and original sanitized reports; rerun dry-run.'}), file=sys.stderr)
        return 1
    except OSError:
        print(report.dump({'status': 'failed', 'failure_class': 'artifact_persistence',
            'message': 'Summary files could not be read or published.',
            'recommended_action': 'Reconcile local paths, lock and metadata; do not repeat business actions.'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
