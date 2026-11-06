#!/usr/bin/env python3
"""Persist an accepted plan-type load receipt locally. Never submits or polls."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import sys

_spec = importlib.util.spec_from_file_location('_ppt_receipt_gate', Path(__file__).with_name('import_preview.py'))
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def build_receipt(envelope, result, content):
    # Local approval/Run Book and exact-byte checks only; no replanning or network.
    verified = gate.verify_archive(envelope, content)
    preview = verified['preview']
    final = preview['finalData']
    binding = preview['runbookBinding']
    if (result.get('initiationStatus') != 'SUCCESS' or result.get('uploadStatus') != 'SUCCESS'):
        raise ValueError('Accepted initiation is required; do not label an uncertain submission successful.')
    request_id, content_id = result.get('RequestId'), result.get('ContentId')
    if (isinstance(request_id, bool) or not re.fullmatch(r'[1-9][0-9]*', str(request_id))
            or not isinstance(content_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', content_id)):
        raise ValueError('Accepted result requires a RequestId and ContentId.')
    filename = Path(final['archivePath']).name
    if result.get('fileName') != filename or result.get('dataSetName', filename) != filename:
        raise ValueError('Accepted result does not identify the approved archive filename.')
    return {'schemaVersion': '1.0', 'taskCode': gate.TASK_CODE,
            'recordedAt': datetime.now(timezone.utc).isoformat(),
            'status': 'initiated', 'completionVerified': False,
            'requestId': str(request_id), 'contentId': content_id,
            'archivePath': final['archivePath'], 'archiveSha256': final['archiveSha256'],
            'environment': final.get('environment'), 'operation': final['operation'],
            'runbookBinding': binding}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--envelope', type=Path, required=True,
                        help='Retained copy of the task-approved envelope, before loader cleanup.')
    parser.add_argument('--result', type=Path, required=True, help='Actual structured loader initiation result.')
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        receipt = build_receipt(json.loads(args.envelope.read_text()),
                                json.loads(args.result.read_text()), args.archive.read_bytes())
        root = Path(receipt['runbookBinding']['projectRoot']).resolve()
        destination = args.output.resolve()
        if not destination.is_relative_to(root / 'artifacts') or not destination.parent.is_dir():
            raise ValueError('Receipt destination must have an existing parent under the bound project artifacts.')
        if destination.exists():
            raise ValueError('Receipt already exists; never overwrite or resubmit an accepted load.')
        if not args.dry_run:
            with destination.open('x') as stream:
                stream.write(json.dumps(receipt, indent=2)+'\n')
        print(json.dumps(receipt, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
