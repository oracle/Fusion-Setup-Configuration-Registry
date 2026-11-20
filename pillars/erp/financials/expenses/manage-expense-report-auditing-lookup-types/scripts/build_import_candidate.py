#!/usr/bin/env python3
"""Prepare an offline, selected type/code FSM candidate. Submission belongs to Data Loader."""
import sys as _artifact_sys
from pathlib import Path as _ArtifactPath
_artifact_sys.path.insert(0, str(_ArtifactPath(__file__).resolve().parent))
from artifact_publication import publish_files, publish_json
import argparse
import csv
import datetime as dt
import re
import hashlib
import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from intake_workbook import ROOT, TASK, TYPE_MEMBER, TYPE_TL_MEMBER, preflight

CONTRACT = json.loads((ROOT / 'references/package-contract.json').read_text())
CODE = 'FUN_APP_GENERIC_LOOKUP.csv'
TRANSLATION = 'FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv'
KEY = ('LookupType', 'LookupCode', 'ViewApplicationId', 'SetCode')
TYPE_KEY = ('LookupType', 'ViewApplicationId')


def package(path):
    with zipfile.ZipFile(path) as z:
        wanted = set(CONTRACT['members']) | {'ASM_SETUP_CSV_METADATA.xml'}
        if set(z.namelist()) != wanted or len(z.namelist()) != len(wanted):
            raise ValueError('Unexpected or duplicate FSM package members.')
        if sum(x.file_size for x in z.infolist()) > 50_000_000:
            raise ValueError('Package exceeds supported size.')
        metadata = z.read('ASM_SETUP_CSV_METADATA.xml')
        xml = ET.fromstring(metadata)
        if xml.findtext('.//ObjectShortName') != TASK or xml.findtext('.//ObjectType') != 'TASK':
            raise ValueError('Wrong task metadata.')
        result = {}
        for name, header in CONTRACT['members'].items():
            rows = list(csv.reader(io.StringIO(z.read(name).decode('utf-8-sig')), strict=True))
            if not rows or rows[0] != header or any(len(r) != len(header) for r in rows):
                raise ValueError('Header order or row width mismatch: ' + name)
            result[name] = [dict(zip(header, r)) for r in rows[1:]]
        return metadata, result


def import_date(value):
    """Normalize only the two observed date-only export/input representations."""
    if value == '':
        return value
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}([/-])\d{2}\1\d{2}', value):
        raise ValueError('Unsupported retained date; require YYYY-MM-DD or YYYY/MM/DD.')
    return dt.date.fromisoformat(value.replace('/', '-')).isoformat()


def validate_import_rows(rows):
    """Reject missing required system values before a candidate reaches Data Loader."""
    for member, records in rows.items():
        for index, row in enumerate(records, start=2):
            if not isinstance(row.get("ChangeSinceLastRefresh"), str) or len(row["ChangeSinceLastRefresh"]) != 1 or not row["ChangeSinceLastRefresh"].strip():
                raise ValueError(f"{member} row {index}: ChangeSinceLastRefresh requires a retained nonblank one-character value.")


def key(row):
    return tuple(str(row.get(k, '')) for k in KEY)


def build(model, snapshot, template, baseline, environment):
    checks = preflight(model, snapshot, environment)
    if checks['status'] != 'ready_for_design_review':
        raise ValueError('Preflight is blocked: ' + json.dumps(checks['issues']))
    metadata, empty = package(template)
    if any(empty.values()):
        raise ValueError('Template package must contain headers only.')
    baseline_metadata, original = package(baseline)
    for label, path in [('template', template), ('baseline', baseline)]:
        if snapshot.get(label + '_sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('Reference evidence is not bound to the exact ' + label + ' package.')
    tm, bm = ET.fromstring(metadata), ET.fromstring(baseline_metadata)
    if any(m.findtext('.//ProcessEnv') != environment for m in (tm, bm)):
        raise ValueError('Export environment does not match the selected destination.')
    if not tm.findtext('.//ProcessRelease') or tm.findtext('.//ProcessRelease') != bm.findtext('.//ProcessRelease'):
        raise ValueError('Template/current export release mismatch.')
    by_key = {}
    for row in original[CODE]:
        if key(row) in by_key:
            raise ValueError('Duplicate baseline identity.')
        by_key[key(row)] = row
    candidate = {name: [] for name in CONTRACT['members']}
    # Types remain existing parents. A modified-only export can omit a seeded
    # parent; a reviewed schema-complete readback can supply its retained row.
    # Never reconstruct omitted target values from shipped seed data.
    type_baselines = list(original[TYPE_MEMBER])
    for evidence in snapshot.get('preservation_rows', {}).get(TYPE_MEMBER, []):
        row = evidence.get('row', {})
        if not evidence.get('source_ref') or set(row) != set(CONTRACT['members'][TYPE_MEMBER]):
            raise ValueError('Type preservation evidence needs a source reference and every package column.')
        matches = [r for r in type_baselines if tuple(str(r[k]) for k in TYPE_KEY) == tuple(str(row[k]) for k in TYPE_KEY)]
        if matches and any(r != row for r in matches):
            raise ValueError('Export and selected-type preservation evidence conflict.')
        if not matches:
            type_baselines.append(row)
    for resolved in checks['resolved_type_rows']:
        if not resolved['changes']:
            continue
        ident = resolved['identity']
        matches = [r for r in type_baselines if tuple(str(r.get(k, '')) for k in TYPE_KEY) == tuple(str(ident[k]) for k in TYPE_KEY)]
        if len(matches) != 1:
            raise ValueError('Existing type is absent from, or ambiguous in, the complete preservation baseline. Do not create it or synthesize its retained fields from seed data.')
        old = matches[0]
        target = next(t for t in snapshot['types'] if t['LookupType'] == ident['LookupType'] and str(t['ViewApplicationId']) == str(ident['ViewApplicationId']))
        for field in ('Meaning', 'Description', 'ModuleId', 'CustomizationLevel'):
            if field not in target or str(target[field] or '') != str(old[field] or ''):
                raise ValueError('Type baseline and fresh destination evidence disagree: ' + field)
        row = dict(old, **resolved['changes'])
        for field in ('CreatedBy', 'CreationDate', 'LastUpdateDate', 'LastUpdateLogin', 'LastUpdatedBy',
                      'DeleteLookupCode', 'DeleteLookupType', 'InsertLookupCode'):
            row[field] = ''
        candidate[TYPE_MEMBER].append(row)
        # Meaning/Description belong to the current-language parent EO. Do not
        # replay its old TL rows over the changed parent text. OA_TL_ENTITIES
        # owns language handling; independent TL authoring is a separate route.
    for resolved in checks['resolved_rows']:
        if resolved['operation'] == 'update' and not resolved['changes']:
            continue
        ident = resolved['identity']
        old = by_key.get(key(ident))
        if resolved['operation'] == 'update' and old is None:
            raise ValueError('Existing code is absent from the customer-modified export. Obtain schema-complete selected-row evidence before packaging; never treat it as new.')
        if resolved['operation'] == 'update' and old is not None:
            # A fresh lookup GET can observe a change made after the FSM export.
            # Never replay stale retained business values from that export.
            set_id = next(s['SetId'] for s in snapshot['sets'] if s['SetCode'] == ident['SetCode'])
            fresh = next(r for r in snapshot['codes']
                         if r['LookupType'] == ident['LookupType']
                         and r['LookupCode'] == ident['LookupCode']
                         and str(r['ViewApplicationId']) == str(ident['ViewApplicationId'])
                         and str(r['SetId']) == str(set_id))
            for field in ('Meaning', 'Description', 'EnabledFlag', 'DisplaySequence',
                          'StartDateActive', 'EndDateActive', 'Tag'):
                if field not in fresh:
                    continue  # An omitted REST field establishes no value.
                retained = old[field]
                current = '' if fresh[field] is None else str(fresh[field])
                if field in ('StartDateActive', 'EndDateActive'):
                    retained, current = import_date(retained), import_date(current)
                if retained != current:
                    raise ValueError('Code baseline and fresh destination evidence disagree: ' + field +
                                     '. Refresh the export and reference evidence before preparing an update.')
        if resolved['operation'] == 'create' and old is not None:
            raise ValueError('Snapshot and baseline disagree about existence.')
        row = dict(old or {h: '' for h in CONTRACT['members'][CODE]})
        row.update({k: str(v) for k, v in ident.items()})
        row.update({k: str(v) for k, v in resolved['changes'].items()})
        row.update(ModuleKey='EXM', ModuleType='APPLICATION')
        if resolved['operation'] == 'create':
            # LookupGenericEO and LookupGenericTranslationEO declare DefaultValue=N.
            # An explicit CSV blank overrides that default and fails EO validation.
            row['ChangeSinceLastRefresh'] = 'N'
        # Audit and transient values are not caller-supplied inputs.
        for field in ('CreatedBy', 'CreationDate', 'LastUpdateDate', 'LastUpdateLogin', 'LastUpdatedBy', 'UpdateStartDate'):
            row[field] = ''
        for field in ('StartDateActive', 'EndDateActive'):
            row[field] = import_date(row.get(field, ''))
        candidate[CODE].append(row)
        # Copy every existing selected-code translation byte value. Translated text
        # must be handled by a separately verified language-aware workflow.
        translations = [r for r in original[TRANSLATION] if tuple(r.get('FUN_APP_GENERIC_LOOKUP.' + k, '') for k in KEY) == key(ident)]
        if translations and any(k in resolved['changes'] for k in ('Meaning', 'Description')):
            raise ValueError('Selected code has translations. Resolve source language and translated text before packaging a meaning/description change.')
        candidate[TRANSLATION].extend(translations)
    if not candidate[CODE] and not candidate[TYPE_MEMBER]:
        raise ValueError('No changed type or code rows; do not submit an empty import.')
    validate_import_rows(candidate)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, header in CONTRACT['members'].items():
            stream = io.StringIO(newline='')
            writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator='\r\n')
            writer.writerow(header)
            writer.writerows([[row.get(h, '') for h in header] for row in candidate[name]])
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            z.writestr(info, stream.getvalue().encode('utf-8'))
        z.writestr(zipfile.ZipInfo('ASM_SETUP_CSV_METADATA.xml', (2020, 1, 1, 0, 0, 0)), metadata)
    return out.getvalue(), checks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('input', 'snapshot', 'template', 'baseline', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--environment', required=True)
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if a.output.exists():
        p.error('Refusing to overwrite output.')
    data, checks = build(json.loads(a.input.read_text()), json.loads(a.snapshot.read_text()), a.template, a.baseline, a.environment)
    print(json.dumps({'status': 'offline_candidate_only', 'code_rows': len(checks['resolved_rows']), 'type_rows': len(checks['resolved_type_rows']), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'execution_authorized': False}))
    if not a.dry_run:
        publish_files({a.output: data})



if __name__ == '__main__':
    main()
