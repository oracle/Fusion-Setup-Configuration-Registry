#!/usr/bin/env python3
"""Run Task Level Export for COA setup and retain UTC freshness observations.

Delegates all catalog/auth/create/poll/download mechanics to the shared skill.
The original Fusion ZIP is unchanged. Receipts are local workflow evidence,
not cryptographic attestations; collect them from an actual new export run.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from xml.etree import ElementTree
import zipfile

TASK_CODE = 'GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES'


def run_export(exporter):
    events = {}
    original = {key: getattr(exporter, key) for key in
                ('parse_args', 'create_export_process', 'wait_for_result', 'write_export_artifact')}
    def parse():
        args = original['parse_args']()
        if args.task_code != TASK_CODE or args.template_only or args.task_name:
            raise ValueError('Use --task-code '+TASK_CODE+' --data for this COA export.')
        return args
    def create(props, token, scope, **kwargs):
        events['startedAt'] = dt.datetime.now(dt.timezone.utc).isoformat()
        return original['create_export_process'](props, token, scope, **kwargs)
    def wait(props, token, scope, process_id, *args):
        result = original['wait_for_result'](props, token, scope, process_id, *args)
        if exporter.process_completed(result[0].get('ProcessCompletedFlag')):
            events['processId'] = str(process_id)
            events['completedAt'] = dt.datetime.now(dt.timezone.utc).isoformat()
        return result
    def write(props, scope, process_id, content, **kwargs):
        path = original['write_export_artifact'](props, scope, process_id, content, **kwargs)
        if kwargs.get('is_log') or not events.get('completedAt'):
            return path
        with zipfile.ZipFile(path) as archive:
            xml = ElementTree.fromstring(archive.read('ASM_SETUP_CSV_METADATA.xml'))
        def field(name):
            values = [x.text or '' for x in xml.iter() if x.tag.rsplit('}', 1)[-1] == name]
            return values[0] if len(values) == 1 else ''
        if field('ObjectShortName') != TASK_CODE or field('ProcessStatus') != 'COMPLETED' or field('ProcessType') != 'EXPORT':
            raise ValueError('Downloaded COA ZIP is not a completed data export.')
        observation = {'schemaVersion': 'invoice-coa-export-observation-v1',
            'source': 'shared.setup-export.task-level-export', 'taskCode': TASK_CODE,
            'status': 'COMPLETED', 'processCompletedFlag': True,
            'environment': field('ProcessEnv'), 'release': field('ProcessRelease'),
            'artifactSha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            **events, 'observedAt': dt.datetime.now(dt.timezone.utc).isoformat()}
        receipt = Path(path).with_name(Path(path).name+'.observation.json')
        with receipt.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(observation, indent=2)+'\n')
        print('COA export observation: '+str(receipt))
        return path
    for key, value in (('parse_args',parse),('create_export_process',create),
                       ('wait_for_result',wait),('write_export_artifact',write)):
        setattr(exporter,key,value)
    try:
        return exporter.main()
    finally:
        for key,value in original.items():
            setattr(exporter,key,value)


def main():
    repo = Path(__file__).resolve().parents[6]
    path = repo/'shared/setup-export/task-level-export/scripts/export_setup_task_csv.py'
    sys.path.insert(0,str(path.parent))
    spec = importlib.util.spec_from_file_location('invoice_coa_shared_export',path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    return run_export(exporter)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        print('COA export failed: '+str(exc),file=sys.stderr)
        raise SystemExit(1)
