#!/usr/bin/env python3
"""Prepare an FSM candidate for maintenance Data Loader preflight and Task Hook.

The historical filename is retained, but no interactive session API is used.
Read one normalized JSON object from stdin. Core owns approval and submission.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import zipfile

from input_contract import (InputError, TASK_CODE, _unique_json_object,
                            combine_requests, split_verified_noops,
                            validate_environment_binding, assess_schedule_visibility)
from fsm_transport import prepare_members, reconcile_option_baseline, qualify_template, METADATA

TASK_NAME = 'Manage Auto Submission and Matching Options'


def validate_input(value, *, qualification_run=False):
    required = {'requests', 'baseline', 'environment_binding'}
    if not isinstance(value, dict) or not required <= set(value) or set(value) - required - {'option_alias_baseline'}:
        raise InputError('Supply requests, baseline, environment_binding and optional option_alias_baseline only.')
    binding = value['environment_binding']
    if not isinstance(binding, dict) or 'requested_url' not in binding:
        raise InputError('ENVIRONMENT_NOT_BOUND: route-owned environment provenance is required.')
    validate_environment_binding(**binding)
    if not isinstance(value['baseline'], list) or not all(isinstance(row, dict) for row in value['baseline']):
        raise InputError('Baseline must contain canonical same-target facts.')
    changes = combine_requests(value['requests'])['changes']
    baseline = value['baseline']
    if 'option_alias_baseline' in value:
        options = reconcile_option_baseline(value['option_alias_baseline'])
        if any(row.get('entity') == 'EXM_SETUP_OPTION' for row in baseline):
            raise InputError('FSM_ALIAS_BASELINE_CONFLICT: supply option facts through the aliases only, without a second baseline.')
        baseline = [*baseline, *options]
    elif qualification_run and any(row['entity'] == 'EXM_SETUP_OPTION' for row in changes):
        raise InputError('FSM_ALIAS_BASELINE_CONFLICT: qualification requires both complete option alias baselines.')
    result = split_verified_noops(changes, baseline)
    result['schedule_visibility'] = assess_schedule_visibility(changes, baseline)
    # Block all required option writes before core setup. Satisfied enablement
    # stays visible in already_satisfied and is never serialized to either alias.
    if not qualification_run and any(row['entity'] != 'EXM_ORG_SETTING' for row in result['changes']):
        raise InputError('FSM_ALIAS_COLLISION: required enable/disable write needs a qualified owning contract.')
    return result


def prepare_candidate(template, value, output=None, *, dry_run=False, qualification_run=False):
    """Compose locally; this result is never a loader preflight or approval."""
    if not isinstance(dry_run, bool) or not isinstance(qualification_run, bool):
        raise InputError('Preparation modes must be explicit booleans.')
    result = validate_input(value, qualification_run=qualification_run)
    report = {**result, 'taskCode': TASK_CODE,
              'environment': value['environment_binding']['requested_url'],
              'qualification_run': qualification_run, 'live_qualification_verified': False,
              'live_checks_performed': False, 'ready_for_import': False}
    if not result['changes']:
        return {**report, 'state': 'already_satisfied'}
    template = Path(template)
    members = prepare_members(template.read_bytes(), result['changes'], qualification_run=qualification_run)
    report['members'] = [name for name, _ in members]
    content_by_name = dict(members)
    profile = qualify_template(content_by_name[METADATA].decode('utf-8-sig'), {
        name: tuple(next(csv.reader(io.StringIO(content.decode('utf-8-sig')))))
        for name, content in members if name != METADATA
    })
    report['transport_profile'] = profile
    report['task_profile'] = profile['option_candidate'] if qualification_run else profile['profile']
    if dry_run:
        return {**report, 'state': 'dry_run'}
    if output is None:
        raise InputError('ARTIFACT_PERSISTENCE: --output is required to prepare a candidate.')
    output = Path(output)
    if (not output.is_absolute() or output.suffix.lower() != '.zip'
            or output.resolve() == template.resolve() or not output.parent.is_dir()):
        raise InputError('ARTIFACT_PERSISTENCE: use a new absolute ZIP path in an existing authorized directory.')
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in members:
            archive.writestr(name, content)
    content = stream.getvalue()
    # Exclusive creation rejects existing files and symlinks, including a
    # previously reviewed or approval-bound candidate. No overwrite option.
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as target:
            target.write(content)
    except BaseException:
        output.unlink()
        raise
    return {**report, 'state': 'candidate_prepared',
            'archivePath': str(output), 'archiveSha256': hashlib.sha256(content).hexdigest(),
            'next_action': 'Run core.data-loader preflight, Task Hook rules and exact-artifact approval before submission.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True, help='Fresh same-target header-only task export ZIP.')
    parser.add_argument('--output', type=Path, help='New absolute candidate ZIP path in an authorized local directory.')
    parser.add_argument('--dry-run', action='store_true', help='Validate input and template locally without writing a candidate.')
    parser.add_argument('--qualify-option-aliases', action='store_true',
                        help='Maintainer-selected non-production qualification of identical option aliases; core preview approval is still required.')
    options = parser.parse_args(argv)
    print(json.dumps({'state': 'awaiting_task_input'}), flush=True)
    try:
        line = sys.stdin.readline(1024 * 1024 + 1)
        if not line or line.strip() == '{"command":"cancel"}':
            print(json.dumps({'state': 'cancelled'}), flush=True)
            return 0
        if len(line) > 1024 * 1024:
            raise InputError('Task input exceeds the supported size.')
        value = json.loads(line, object_pairs_hook=_unique_json_object)
        if value == {'command': 'cancel'}:
            print(json.dumps({'state': 'cancelled'}), flush=True)
            return 0
        report = prepare_candidate(options.template, value, options.output,
                                   dry_run=options.dry_run,
                                   qualification_run=options.qualify_option_aliases)
        print(json.dumps(report), flush=True)
        return 0
    except (InputError, ValueError, TypeError, KeyError, OSError) as exc:
        # No customer values, credentials or raw decoder exceptions in errors.
        code = str(exc).split(':', 1)[0]
        if isinstance(exc, OSError):
            code = 'ARTIFACT_PERSISTENCE'
        if code not in {'FSM_ALIAS_COLLISION', 'FSM_ALIAS_BASELINE_CONFLICT', 'FSM_SCHEMA_MISMATCH', 'ENVIRONMENT_NOT_BOUND', 'ENVIRONMENT_MISMATCH', 'ARTIFACT_PERSISTENCE'}:
            code = 'INPUT_VALIDATION'
        print(json.dumps({'state': 'failure', 'stage': 'artifact-persistence' if code == 'ARTIFACT_PERSISTENCE' else 'input-validation',
                          'code': code,
                          'message': 'Check task input, template, environment binding and the new candidate output path.'}), flush=True)
        return 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
