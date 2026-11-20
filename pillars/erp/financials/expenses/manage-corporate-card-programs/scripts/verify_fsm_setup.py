"""Compare trusted same-target FSM exports; no network calls or load-status claims."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import zipfile
import csv
import xml.etree.ElementTree as ET

from prepare_fsm_package import inspect_package, normalize_design, ROOT, HEADERS


def verify_setup(baseline, after, design, environment):
    _, before, release = inspect_package(baseline, environment)
    _, current, after_release = inspect_package(after, environment)
    if release != after_release:
        raise ValueError('Baseline and verification export releases differ')
    expected, _, derived = normalize_design(design)
    root = expected[ROOT]
    name = root['CardProgramName']
    if any(row['CardProgramName'].strip().casefold() == name.strip().casefold()
           for row in before[ROOT]):
        raise ValueError('Baseline already contains the requested CREATE name')
    findings = []
    checked = 0
    def belongs(entity, row):
        key = 'CardProgramName' if entity == ROOT else 'EXM_CARD_PROGRAM.CardProgramName'
        return row.get(key, '').strip().casefold() == name.strip().casefold()
    for entity, headers in HEADERS.items():
        candidates = [row for row in current[entity] if belongs(entity, row)]
        if entity in expected:
            if len(candidates) != 1:
                findings.append({'entity': entity, 'issue': 'requested_row_count',
                                 'expected': 1, 'actual': len(candidates)})
            else:
                for field, value in expected[entity].items():
                    checked += 1
                    if candidates[0].get(field) != value:
                        # No customer field values in diagnostic output.
                        findings.append({'entity': entity, 'field': field,
                                         'issue': 'value_mismatch'})
        elif candidates:
            findings.append({'entity': entity, 'issue': 'unexpected_child_rows',
                             'actual': len(candidates)})
        # Compare multisets to retain duplicates, full headers and blank columns.
        # Exclude only new program rows; all prior issuer/site/download rows are protected.
        def counts(rows):
            return Counter(tuple(row[field] for field in headers) for row in rows)
        old = counts(before[entity])
        remaining = counts(row for row in current[entity] if not belongs(entity, row))
        if old != remaining:
            findings.append({'entity': entity, 'issue': 'protected_rows_changed',
                             'removed': sum((old - remaining).values()),
                             'added': sum((remaining - old).values())})
    return {'status': 'failed' if findings else 'passed',
            'scope': 'exported_setup_values_and_baseline_preservation',
            'checkedFields': checked, 'derivedFields': derived,
            'loadStatusVerified': False, 'credentialPreservation': 'NOT_VERIFIED', 'errors': findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--environment', required=True)
    args = parser.parse_args()
    try:
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('Duplicate input key')
                result[key] = value
            return result
        design = json.loads(args.input.read_text(), object_pairs_hook=unique)
        report = verify_setup(args.baseline, args.after, design, args.environment)
        code = 0 if report['status'] == 'passed' else 1
    except (ValueError, OSError, zipfile.BadZipFile, ET.ParseError, csv.Error):
        report = {'status': 'blocked', 'failure_class': 'input_validation',
                  'message': 'Invalid or unreadable design/export; check identity, metadata, headers and provenance.',
                  'loadStatusVerified': False}
        code = 2
    print(json.dumps(report, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
