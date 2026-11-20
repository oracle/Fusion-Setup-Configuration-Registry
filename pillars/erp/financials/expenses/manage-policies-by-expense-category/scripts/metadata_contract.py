"""Compare exported metadata by owning table; preserve submission metadata exactly.

Sequence drift between exports is reported separately from schema/ownership
drift. Neither classification authorizes changing a submission descriptor.
"""
from collections import Counter
import json
from pathlib import Path

from workbook_intake import IntakeError, checked_zip, sha256, xml


def descriptor(path):
    with checked_zip(path) as archive:
        members = [n for n in archive.namelist() if Path(n).name == 'ASM_SETUP_CSV_METADATA.xml']
        if len(members) != 1:
            raise IntakeError('Exactly one FSM metadata descriptor is required')
        return archive.read(members[0])


def snapshot(path, entities, *, strict_inventory=False):
    """Keep table identity and duplicate records; do not collapse by entity."""
    root = xml(descriptor(path))
    records = []
    def visit(node, parents):
        name = node.tag.rsplit('}', 1)[-1]
        fields = {}
        for child in node:
            if list(child):
                continue
            key = child.tag.rsplit('}', 1)[-1]
            if key in fields:
                raise IntakeError('Duplicate metadata attribute in one record')
            fields[key] = child.text
        if (strict_inventory and name in {'MigrationProcessBusinessObjectCSVMetadataVORow',
                'MigrationProcessMigrationObjectCSVMetadataVORow'}
                and not fields.get('BusinessObjectShortName')):
            raise IntakeError('Metadata object identity is missing')
        if (strict_inventory and 'BusinessObjectShortName' in fields
                and fields['BusinessObjectShortName'] not in entities):
            raise IntakeError('Unexpected business object metadata: '+str(fields['BusinessObjectShortName']))
        if fields.get('BusinessObjectShortName') in entities:
            fields = {k: v for k, v in fields.items() if not k.startswith('Process')}
            if 'NodeSequence' in fields:
                sequence = fields['NodeSequence']
                if not isinstance(sequence, str) or not sequence.isascii() or not sequence.isdecimal() or int(sequence) < 1:
                    raise IntakeError('Invalid metadata NodeSequence')
            records.append({'table': '/'.join(parents + [name]), 'fields': fields})
        for child in node:
            visit(child, parents + [name])
    visit(root, [])
    covered = {record['fields']['BusinessObjectShortName'] for record in records}
    if covered != set(entities):
        raise IntakeError('Selected entity metadata is missing')
    return records


def _counts(records, *, omit_sequence=False):
    values = []
    for record in records:
        fields = dict(record['fields'])
        if omit_sequence:
            fields.pop('NodeSequence', None)
        values.append(json.dumps({'table': record['table'], 'fields': fields}, sort_keys=True))
    return Counter(values)


def compare(before, after, entities, sequence_policy=None):
    a, b = snapshot(before, entities, strict_inventory=True), snapshot(after, entities, strict_inventory=True)
    left, right = _counts(a), _counts(b)
    equal = left == right
    sequence_only = not equal and _counts(a, omit_sequence=True) == _counts(b, omit_sequence=True)
    reviewed_local = (isinstance(sequence_policy, dict)
        and set(sequence_policy) == {'mode', 'sourceEvidence', 'xmlFileByEntity'}
        and sequence_policy['mode'] == 'export-local'
        and isinstance(sequence_policy['sourceEvidence'], list) and bool(sequence_policy['sourceEvidence'])
        and all(isinstance(s, str) and s.strip() for s in sequence_policy['sourceEvidence'])
        and isinstance(sequence_policy['xmlFileByEntity'], dict)
        and set(sequence_policy['xmlFileByEntity']) == set(entities)
        and all(isinstance(v, str) and v.strip() for v in sequence_policy['xmlFileByEntity'].values()))
    if sequence_policy is not None and not reviewed_local:
        raise IntakeError('Invalid reviewed export-local metadata policy')
    compatible = equal or (sequence_only and reviewed_local)
    status = ('EXACT_METADATA_MATCH' if equal else
              'REVIEWED_EXPORT_LOCAL_SEQUENCE_CHANGE' if compatible else
              'SEQUENCE_DRIFT_REQUIRES_FRESH_DESCRIPTOR' if sequence_only else
              'STRUCTURAL_METADATA_DRIFT_STOP')
    return {'status': status, 'exact': equal, 'compatible': compatible, 'sequence_only': sequence_only,
            'before_records': len(a), 'after_records': len(b),
            'removed_records': [json.loads(v) for v in (left-right).elements()],
            'added_records': [json.loads(v) for v in (right-left).elements()],
            'sequence_policy': sequence_policy,
            'submission_policy': 'Preserve the chosen fresh baseline descriptor byte-for-byte. Only an explicit source-reviewed export-local policy admits verification sequence changes; never reorder metadata.'}


def verify_submission_metadata(baseline, candidate):
    original, submitted = descriptor(baseline), descriptor(candidate)
    if original != submitted:
        raise IntakeError('Candidate metadata must remain byte-identical to its bound baseline')
    return {'status': 'EXACT_BOUND_DESCRIPTOR_PRESERVED', 'sha256': sha256(original)}
