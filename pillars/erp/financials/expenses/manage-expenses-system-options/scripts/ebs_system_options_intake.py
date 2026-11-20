"""Reassess source-bound EBS decisions and plan cells for the owning workbook.

Local only. Called by the task's from-ebs command; stdout is captured by that
command, never used as an import artifact. No Fusion calls or guessed mappings.
"""
import argparse
import json
from pathlib import Path
import sys

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL.parent / 'scripts'))
import ebs_profile_intake as intake


def prepare(raw, environment, decisions):
    report = intake.assess(raw, environment, decisions)
    catalog = json.loads((SKILL / 'references/intake-fields.json').read_text())
    report['workbook_cells'] = []
    if report['status'] != 'ready_for_task_intake':
        return report
    row_numbers = {}
    for item in report['task_inputs']:
        intake.require(item['task_code'] == catalog['source_export']['task_code'],
                       'Input contains another task; route it separately before workbook generation')
        matches = [(section, i, field) for section in catalog['sections']
                   for i, field in enumerate(section['fields'], 2)
                   if field['source'] == 'EXM_SETUP_OPTION' and field['code'] == item['OptionCode']
                   and field['mapping'] == 'confirmed']
        intake.require(len(matches) == 1, 'Require exactly one confirmed workbook field')
        section, column, field = matches[0]
        if field['kind'] == 'yes_no':
            labels = {'Y': 'Yes', 'N': 'No'}
            intake.require(item['ValueCode'] in labels, 'Unknown boolean value')
            label = labels[item['ValueCode']]
        elif field['kind'] == 'enum':
            labels = [c['label'] for c in field['choices'] if c['code'] == item['ValueCode']]
            intake.require(len(labels) == 1, 'Require a unique confirmed dropdown value')
            label = labels[0]
        else:
            raise ValueError('This EBS adapter supports confirmed option dropdowns only')
        key = (section['sheet'], item['BuName'])
        if key not in row_numbers:
            row_numbers[key] = 5 + sum(k[0] == key[0] for k in row_numbers)
        intake.require(row_numbers[key] <= 504, 'Workbook capacity exceeded')
        report['workbook_cells'].append({'sheet': section['sheet'], 'row': row_numbers[key],
            'column': column, 'business_unit': item['BuName'], 'value': label,
            'field_key': field['key'], 'source_record_ids': item['source_record_ids']})
    report['field_catalog_sha256'] = intake.digest((SKILL / 'references/intake-fields.json').read_bytes())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--decisions', type=Path, required=True)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--project-root', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        report = prepare(args.input.read_bytes(), args.environment, json.loads(args.decisions.read_text()))
        if args.output or args.report:
            intake.require(args.project_root and args.output and args.report, 'Both outputs and project root are required')
            paths = intake.module('artifact_paths', intake.REPO / 'core/project-mgmt/artifact-registry-manager/scripts/project_artifact_paths.py')
            intake.require(args.output.resolve() != args.report.resolve(), 'Outputs must be distinct')
            for output in (args.output, args.report):
                paths.validate_artifact_path(output.absolute(), args.project_root.absolute())
        print(json.dumps(report))
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print(json.dumps(intake.failure(error, 'system_options_ebs_intake')))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
