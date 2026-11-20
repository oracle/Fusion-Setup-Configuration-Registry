"""Local EBS profile CSV intake and task routing; never calls Fusion.

All profiles are accounted for. Only maintained mappings produce task inputs;
unknown profiles produce questions, not guessed FSM columns. Decisions are
bound to the source bytes and environment and are not import approval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re

EXPENSES = Path(__file__).resolve().parents[1]
REPO = EXPENSES.parents[3]
CATALOG = EXPENSES / 'references/ebs-profile-mappings.json'
HEADERS = {'APPLICATION_ID', 'PROFILE_OPTION_ID', 'PROFILE_OPTION_NAME',
           'USER_PROFILE_OPTION_NAME', 'DESCRIPTION', 'LEVEL_ID', 'LEVEL_VALUE',
           'LEVEL_VALUE_APPLICATION_ID', 'PROFILE_OPTION_VALUE'}
IDENTITY = ('APPLICATION_ID', 'PROFILE_OPTION_ID', 'PROFILE_OPTION_NAME',
            'LEVEL_ID', 'LEVEL_VALUE', 'LEVEL_VALUE_APPLICATION_ID')
LEVELS = {'10001': 'site', '10002': 'application', '10003': 'responsibility', '10004': 'user'}
SENSITIVE = re.compile(r'PASSWORD|SECRET|TOKEN|PRIVATE.?KEY|CREDENTIAL', re.I)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_source(raw):
    require(raw and len(raw) <= 10 * 1024 * 1024 and b'\0' not in raw,
            'Empty, binary or oversized source CSV')
    reader = csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
    headers = next(reader)
    require(len(headers) == len(HEADERS) and set(headers) == HEADERS,
            'Expected exactly the nine EBS profile extract columns')
    groups = {}
    count = 0
    for number, cells in enumerate(reader, 1):
        require(len(cells) == len(headers), 'Source CSV row width mismatch')
        row = dict(zip(headers, cells))
        require(not SENSITIVE.search(row['PROFILE_OPTION_NAME'] + ' ' + row['USER_PROFILE_OPTION_NAME']),
                'Credential-like profile: remove sensitive profiles from this setup extract')
        require(all(row[k].strip() for k in IDENTITY if k != 'LEVEL_VALUE_APPLICATION_ID'),
                'Missing source identity')
        require(all(row[k].isdigit() for k in ('APPLICATION_ID', 'PROFILE_OPTION_ID', 'LEVEL_ID', 'LEVEL_VALUE'))
                and (not row['LEVEL_VALUE_APPLICATION_ID'] or row['LEVEL_VALUE_APPLICATION_ID'].isdigit()),
                'Source IDs must be nonnegative numeric strings')
        key = tuple(row[k] for k in IDENTITY)
        rid = digest(json.dumps(key, separators=(',', ':')).encode())[:24]
        if rid not in groups:
            groups[rid] = {'record_id': rid, 'source': row, 'source_records': [], 'variants': []}
        group = groups[rid]
        group['source_records'].append(number)
        if row not in group['variants']:
            group['variants'].append(row)
        count += 1
    require(count, 'No source records')
    return count, list(groups.values())


def load_mappings():
    catalog = json.loads(CATALOG.read_text())
    require(catalog.get('version') == 1, 'Unsupported mapping catalog')
    keys = set()
    for entry in catalog['mappings']:
        key = (entry['application_id'], entry['profile_option_name'])
        require(key not in keys and entry.get('evidence'), 'Ambiguous or unsourced maintained mapping')
        keys.add(key)
        task = EXPENSES / entry['task_folder'] / 'SKILL.md'
        require(task.parent.parent == EXPENSES and task.is_file(), 'Unknown owning task')
        require(f'task_code: "{entry["task_code"]}"' in task.read_text(), 'Task catalog identity mismatch')
    return catalog


def assess(raw, environment, decisions=None, catalog=None):
    require(isinstance(environment, str) and environment.strip(), 'Environment is required')
    count, groups = read_source(raw)
    catalog = catalog if catalog is not None else load_mappings()
    decisions = {} if decisions is None else decisions
    require(isinstance(decisions, dict), 'Decisions must be an object')
    if decisions:
        require(decisions.get('source_sha256') == digest(raw)
                and decisions.get('environment') == environment,
                'Decisions do not match source bytes and environment')
        require(set(decisions) <= {'source_sha256', 'environment', 'records'}, 'Unknown decision fields')
    choices = decisions.get('records', {})
    require(isinstance(choices, dict) and set(choices) <= {g['record_id'] for g in groups},
            'Unknown source record in decisions')
    issues, questions, records, candidates = [], [], [], []
    for group in groups:
        rid, row = group['record_id'], group['source']
        decision = choices.get(rid, {})
        require(isinstance(decision, dict) and set(decision) <= {
            'action', 'confirmation_ref', 'reason', 'target_business_units',
            'mapping_proposal', 'tax_field_behavior'}, 'Unknown record decision fields')
        record = {**group, 'scope_level': LEVELS.get(row['LEVEL_ID'], 'unrecognized'),
                  'decision': decision, 'status': 'needs_confirmation'}
        records.append(record)

        def issue(code, message):
            issues.append({'record_id': rid, 'code': code, 'message': message})

        def question(kind, message, options):
            questions.append({'id': f'{rid}:{kind}', 'record_id': rid, 'question': message,
                              'options': options})

        if len(group['variants']) != 1:
            issue('conflicting_source_identity', 'Different values or metadata share one source identity; resolve the extract.')
            record['status'] = 'conflicting_source'
            continue
        if decision:
            require(decision.get('action') in {'migrate', 'exclude'}
                    and isinstance(decision.get('confirmation_ref'), str)
                    and decision['confirmation_ref'].strip(), 'Record decisions require explicit action and confirmation reference')
        if decision.get('action') == 'exclude':
            require(isinstance(decision.get('reason'), str) and decision['reason'].strip(),
                    'Exclusion needs a reason')
            record['status'] = 'excluded_by_user'
            continue
        matches = [m for m in catalog['mappings'] if
                   m['application_id'] == row['APPLICATION_ID'] and
                   m['profile_option_name'] == row['PROFILE_OPTION_NAME']]
        require(len(matches) <= 1, 'Ambiguous maintained mapping')
        if not matches:
            hint = next((h for h in catalog.get('discovery_hints', [])
                         if h['display_name'].casefold() == row['USER_PROFILE_OPTION_NAME'].casefold()), None)
            record['discovery_hint'] = hint
            record['status'] = 'requires_mapping_review'
            issue('unmapped_profile', 'No maintained exact mapping; a proposed mapping or user approval is not technical evidence.')
            question('mapping', f'For {row["PROFILE_OPTION_NAME"]} ({row["USER_PROFILE_OPTION_NAME"]}), '
                     'what behavior must Fusion preserve? Research the owning task and value mapping, or explicitly exclude this profile.',
                     ['Research equivalent and confirm intended behavior', 'Exclude with reason'])
            continue
        mapping = matches[0]
        record['mapping'] = mapping
        if decision.get('mapping_proposal'):
            issue('mapping_override', 'A project proposal cannot override a maintained mapping; request an authoring review.')
        value = row['PROFILE_OPTION_VALUE']
        if value not in mapping['value_map']:
            issue('unmapped_value', 'Blank or unrecognized source value needs semantic review; no guessed boolean/default.')
            question('value', 'What behavior does this source value represent, and what should Fusion preserve?',
                     ['Research source value semantics', 'Exclude with reason'])
        if row['LEVEL_ID'] not in LEVELS:
            issue('unsupported_scope', 'Unrecognized EBS hierarchy level; resolve its meaning before mapping scope.')
        targets = decision.get('target_business_units', [])
        require(isinstance(targets, list) and all(isinstance(t, str) and t.strip() == t and t for t in targets)
                and len(targets) == len(set(targets)), 'BU mappings must be unique nonblank exact names')
        require(not any(t.casefold() == 'all business units' for t in targets),
                'Use explicit named BUs; source site scope is not a global Fusion fallback')
        if not targets or decision.get('action') != 'migrate':
            issue('scope_confirmation_required', 'Explicit mapping from this EBS scope to target named BUs is missing.')
            question('scope', f'Which Fusion business units in {environment} should inherit '
                     f'{row["PROFILE_OPTION_NAME"]} at EBS {record["scope_level"]} scope '
                     f'(level value {row["LEVEL_VALUE"]}, application {row["LEVEL_VALUE_APPLICATION_ID"] or "unspecified"})? '
                     'Confirm exact names or exclude; these IDs are not Fusion BU IDs. '
                     'The target setting applies BU-wide, so confirm whether that preserves the intended '
                     'behavior or needs redesign for responsibility/user-specific restrictions.',
                     ['Map to named business units', 'Resolve EBS responsibility/operating-unit scope', 'Exclude with reason'])
        behavior = decision.get('tax_field_behavior')
        if mapping.get('confirmation') == 'tax_field_behavior':
            if not behavior:
                issue('behavior_confirmation_required', 'Tax enablement does not define country or per-field display behavior.')
                question('behavior', 'For these BUs, should migration change only the tax switch and preserve existing tax-field rules, '
                         'or also configure tax-field behavior? Y does not imply Required. '
                         'New rules need countries (or explicit OTHER), all six Hidden/Optional/Required choices and the rule enabled flag.',
                         ['Switch only; preserve existing rules and review visibility', 'Configure explicit tax-field rules', 'Defer or exclude'])
            else:
                require(isinstance(behavior, dict) and set(behavior) <= {'mode', 'requirements_ref'}
                        and behavior.get('mode') in {'preserve_existing', 'configure_explicit'}, 'Invalid tax behavior decision')
                if behavior['mode'] == 'configure_explicit':
                    issue('tax_rules_intake_required', 'Use the owning Tax rules workbook for explicit rules; this profile adapter never fabricates them.')
                    question('tax_rules', 'Provide the Tax rules workbook or explicit per-BU country and six field choices; '
                             'keep this request pending until its task validator accepts them.', ['Provide tax-rule requirements', 'Switch only; preserve existing rules'])
        if not any(i['record_id'] == rid for i in issues):
            record['status'] = 'ready_for_task_intake'
            for bu in targets:
                candidates.append({'task_code': mapping['task_code'], 'task_folder': mapping['task_folder'],
                                   'BuName': bu, 'OptionCode': mapping['target_code'],
                                   'ValueCode': mapping['value_map'][value],
                                   'source_record_ids': [rid], 'tax_field_behavior': behavior})
    merged = {}
    for row in candidates:
        key = (row['task_code'], row['BuName'], row['OptionCode'])
        if key in merged:
            existing = merged[key]
            if (row['ValueCode'], row['tax_field_behavior']) != (existing['ValueCode'], existing['tax_field_behavior']):
                issues.append({'record_id': row['source_record_ids'][0], 'code': 'conflicting_target',
                               'message': 'Different source scopes map incompatible intent to one target; do not choose a winner.'})
            existing['source_record_ids'].extend(row['source_record_ids'])
        else:
            merged[key] = row
    ready = not issues
    status = 'ready_for_task_intake' if ready and merged else 'no_requested_changes' if ready else 'needs_input'
    return {'schema_version': 1, 'status': status,
            'environment': environment, 'source_sha256': digest(raw), 'record_count': count,
            'distinct_identity_count': len(groups), 'records': records, 'issues': issues,
            'questions': questions, 'task_inputs': list(merged.values()) if ready else [],
            'ready_for_import': False, 'live_checks_performed': False,
            'decisions_sha256': digest(json.dumps(decisions, sort_keys=True).encode()),
            'mapping_catalog_sha256': digest(json.dumps(catalog, sort_keys=True).encode()),
            'next_action': 'No import action: all source assignments explicitly excluded.' if status == 'no_requested_changes'
            else 'Use owning task validation, fresh baseline/reference evidence and core Data Loader approval.' if ready
            else 'Ask the unresolved questions together; record explicit answers and rerun. No partial import unless other rows are explicitly excluded.'}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def persist_report(report, output, project, inputs, skill_id='erp.financials.expenses', extra_artifacts=()):
    paths = module('artifact_paths', REPO / 'core/project-mgmt/artifact-registry-manager/scripts/project_artifact_paths.py')
    paths.validate_artifact_path(output, project)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    logger = module('token_logger', REPO / 'core/project-mgmt/scripts/token_usage_logger.py')
    logger.append_token_usage_log(project_id=project.name, skill_id=skill_id,
        task='EBS profile local intake', trigger='Explicit profile migration intake',
        activity_start_time=logger.utc_now(), artifact_paths=[output, *extra_artifacts], files_read=len(inputs),
        estimated_input_tokens=sum(p.stat().st_size // 4 for p in inputs), root=REPO,
        estimated_output_tokens=output.stat().st_size // 4,
        notes='Local only; file chars/4 estimate. Host registers report and durable run before handoff.')


def failure(error, stage):
    category = 'artifact_persistence' if isinstance(error, OSError) else 'input_validation'
    if str(error).startswith('catalog mismatch:'):
        category = 'catalog_or_metadata_mismatch'
    return {'status': 'blocked', 'stage': stage, 'failure_class': category,
            'message': 'Inspect source/decisions, maintained contracts and project paths locally; no import attempted. '
                       'Do not upload partial artifacts after a persistence failure.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--decisions', type=Path)
    parser.add_argument('--project-root', type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        decisions = json.loads(args.decisions.read_text()) if args.decisions else None
        report = assess(args.input.read_bytes(), args.environment, decisions)
        if args.output:
            require(args.project_root is not None, 'Project root is required for persisted output')
            persist_report(report, args.output.absolute(), args.project_root.absolute(),
                           [args.input, CATALOG] + ([args.decisions] if args.decisions else []))
        # Profile values can be sensitive. Detailed findings stay in the project.
        print(json.dumps({k: report[k] for k in ('status', 'record_count', 'distinct_identity_count',
                                               'ready_for_import', 'live_checks_performed')} |
                         {'issue_count': len(report['issues']), 'question_count': len(report['questions'])}))
        return 0 if report['status'] in {'ready_for_task_intake', 'no_requested_changes'} else 2
    except (ValueError, OSError, UnicodeError, csv.Error, StopIteration) as error:
        print(json.dumps(failure(error, 'profile_intake')))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
