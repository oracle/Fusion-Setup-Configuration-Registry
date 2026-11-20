"""Build a review-only tax-switch candidate from source-bound EBS decisions.

No REST, authentication, upload or approval. The owning workflow verifies
baseline provenance/freshness and target BU references before invoking this.
Standalone N-to-Y updates remain controlled tests until live qualification.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


HERE = Path(__file__).resolve().parent
aliases = load('tax_aliases', HERE / 'tax_option_aliases.py')
intake = load('ebs_profiles', HERE.parents[1] / 'scripts/ebs_profile_intake.py')


def csv_bytes(header, rows):
    text = io.StringIO(newline='')
    writer = csv.DictWriter(text, fieldnames=header, lineterminator='\r\n')
    writer.writeheader()
    writer.writerows(rows)
    return text.getvalue().encode()


def prepare(raw, environment, decisions, baseline, qualification=None):
    assessment = intake.assess(raw, environment, decisions)
    intake.require(assessment['status'] == 'ready_for_task_intake',
                   'EBS intake decisions are unresolved; rerun profile intake')
    requested = assessment['task_inputs']
    if qualification:
        intake.require(isinstance(qualification, dict), 'Qualification decision must be an object')
        intake.require(qualification.get('environment') == environment
                       and qualification.get('source_sha256') == assessment['source_sha256']
                       and qualification.get('decisions_sha256') == assessment['decisions_sha256']
                       and qualification.get('baseline_sha256') == intake.digest(baseline),
                       'Qualification decision is stale or belongs to different scope')
    intake.require(requested and all(r['task_code'] == 'EXM_MANAGE_TAX_FIELDS' and
                   r['OptionCode'] == 'ENABLE_TAX' and r['tax_field_behavior'] == {'mode': 'preserve_existing'}
                   for r in requested), 'Use the owning task for mixed or explicit tax-rule requests')
    members, headers, rows = aliases.read_package(baseline)
    # This also rejects malformed/unsafe XML, before parsing its task identity.
    fingerprint = aliases.schema_fingerprint(baseline)
    meta = ET.fromstring(members[aliases.META].decode('utf-8-sig'))
    tasks = [e.text for e in meta.iter() if e.tag.rsplit('}', 1)[-1] == 'ObjectShortName']
    intake.require(tasks == ['EXM_MANAGE_TAX_FIELDS'], 'Wrong baseline task')
    before = aliases.baseline_options(rows)
    aliases.index(rows[aliases.VAT], aliases.VAT)
    changes, operations = [], []
    for row in requested:
        bu = row['BuName']
        old = before.get((bu, 'ENABLE_TAX'))
        intake.require(old is None or old['ValueCode'] in {'Y', 'N'}, 'Ambiguous baseline switch value')
        operation = 'already_satisfied' if old and old['ValueCode'] == row['ValueCode'] else 'update' if old else 'create'
        rules = [r for r in rows[aliases.VAT] if r['BuName'] == bu]
        operations.append({'BuName': bu, 'operation': operation,
                           'before': old['ValueCode'] if old else None, 'after': row['ValueCode'],
                           'source_record_ids': row['source_record_ids'],
                           'existing_tax_rule_count': len(rules),
                           'visibility_review_required': True,
                           'tax_rule_action': 'preserve; no source field behaviors supplied'})
        if operation != 'already_satisfied':
            changes.append({'BuName': bu, 'OptionCode': 'ENABLE_TAX', 'ValueCode': row['ValueCode'],
                            'OtherOrgId': old['OtherOrgId'] if old else '', **dict.fromkeys(aliases.AUDIT, '')})
    report = {'status': 'already_satisfied' if not changes else 'review_required',
              'environment': environment, 'source_sha256': assessment['source_sha256'],
              'decisions_sha256': assessment['decisions_sha256'],
              'mapping_catalog_sha256': assessment['mapping_catalog_sha256'],
              'baseline_sha256': hashlib.sha256(baseline).hexdigest(),
              'schema_sha256': fingerprint, 'operations': operations,
              'ready_for_import': False, 'live_import_verified': False,
              'target_reference_verified': False, 'baseline_provenance_verified': False,
              'questions': [], 'qualification': qualification}
    if not changes:
        return None, report
    replacements = {name: csv_bytes(headers[name], changes) for name in (aliases.SETUP, aliases.CASH)}
    replacements[aliases.VAT] = csv_bytes(headers[aliases.VAT], [])
    candidate = aliases.replace_members(baseline, replacements)
    active = [r for r in operations if r['operation'] != 'already_satisfied']
    standalone_update = len(active) == 1 and active[0]['operation'] == 'update' and active[0]['before'] == 'N' and active[0]['after'] == 'Y'
    if standalone_update:
        if not qualification:
            report['status'] = 'qualification_required'
            report['questions'] = [{
                'id': 'standalone-tax-update-qualification',
                'question': 'This existing switch needs N-to-Y with no tax-rule change. '
                            'Select a controlled nonproduction qualification and restoration/retention intent, '
                            'or defer it. This is not a routinely qualified update.',
                'options': ['Controlled nonproduction qualification', 'Defer update']}]
            return None, report
        intake.require(isinstance(qualification, dict) and qualification.get('nonproduction') is True
                       and isinstance(qualification.get('confirmation_ref'), str)
                       and qualification['confirmation_ref'].strip()
                       and qualification.get('after_test') in {'retain', 'restore'},
                       'Qualification needs nonproduction confirmation and explicit retain/restore intent')
        candidate, detail = aliases.prepare_qualification(baseline, candidate, qualification_run=True)
        report.update(status='qualification_candidate_review_only', helper=detail)
    else:
        intake.require(qualification is None, 'Standalone update qualification cannot broaden other operation shapes')
        candidate, detail = aliases.prepare_qualified(baseline, candidate)
        report.update(status='candidate_review_only', helper=detail)
    report['candidate_sha256'] = hashlib.sha256(candidate).hexdigest()
    report['next_action'] = 'Evaluate task rules and reference/provenance evidence, review visibility, then use core Data Loader preview and immutable approval. Reconcile ProcessLog and fresh export after execution.'
    return candidate, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--decisions', required=True, type=Path)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--baseline-zip', required=True, type=Path)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--qualification-decision', type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--output-zip', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        project = args.project_root.absolute()
        paths = intake.module('artifact_paths', intake.REPO / 'core/project-mgmt/artifact-registry-manager/scripts/project_artifact_paths.py')
        # Validate project identity even for a no-write run, without reserving a file.
        paths.validate_artifact_path(project / 'artifacts' / 'ebs-tax-preflight-unused.json', project)
        intake.require(args.baseline_zip.resolve().is_relative_to(project / 'exports'), 'Baseline must be a current-project export')
        intake.require(bool(args.output_zip) == bool(args.report), 'A written candidate requires a new companion report; dry-run writes neither')
        if args.output_zip:
            paths.validate_artifact_path(args.output_zip.absolute(), project)
            paths.validate_artifact_path(args.report.absolute(), project)
            intake.require(args.output_zip.absolute() != args.report.absolute(), 'Distinct ZIP and report paths required')
        qualification = json.loads(args.qualification_decision.read_text()) if args.qualification_decision else None
        decisions = json.loads(args.decisions.read_text())
        if qualification:
            intake.require(isinstance(qualification, dict), 'Qualification decision must be an object')
            intake.require(qualification.get('environment') == args.environment and
                           qualification.get('source_sha256') == intake.digest(args.input.read_bytes()) and
                           qualification.get('baseline_sha256') == intake.digest(args.baseline_zip.read_bytes()),
                           'Qualification decision does not match source, environment and baseline')
        candidate, report = prepare(args.input.read_bytes(), args.environment, decisions,
                                    args.baseline_zip.read_bytes(), qualification)
        if args.output_zip and candidate is not None:
            paths.validate_artifact_path(args.output_zip.absolute(), project)
            args.output_zip.parent.mkdir(parents=True, exist_ok=True)
            with args.output_zip.open('xb') as handle:
                handle.write(candidate)
        if args.report:
            inputs = [args.input, args.decisions, args.baseline_zip]
            intake.persist_report(report, args.report.absolute(), project, inputs,
                                  'erp.financials.expenses.manage-tax-fields',
                                  [args.output_zip.absolute()] if candidate is not None else [])
        print(json.dumps({'status': report['status'], 'operation_count': len(report['operations']),
                          'candidate_written': bool(args.output_zip and candidate),
                          'ready_for_import': False, 'live_import_verified': False}))
        return 2 if report['status'] == 'qualification_required' else 0
    except (ValueError, OSError, UnicodeError, csv.Error, StopIteration) as error:
        print(json.dumps(intake.failure(error, 'ebs_tax_candidate')))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
