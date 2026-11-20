"""Bind the bounded pinned DOM proof to each source-qualified create graph."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'PINNED-FSM-DOM-EMPTY-ELEMENT'
STATUS = 'CONFIRMED_PINNED_DEFAULT_ORACLE_PROVIDER_NO_CHILD_PATH'
SERIALIZATIONS = (
    'SHARED-FSM-AIRFARE-CREATE-SERIALIZATION',
    'MILEAGE-CREATE-SERIALIZATION',
    'MISCELLANEOUS-CREATE-SERIALIZATION',
    'PER-DIEM-CREATE-SERIALIZATION',
)


def validate(contract):
    path = ROOT / 'references/fsm-dom-empty-element-contract.json'
    source = contract.get('sources', {}).get(SOURCE, {})
    if (source.get('path') != 'references/fsm-dom-empty-element-contract.json'
            or source.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest()):
        raise ValueError('Pinned DOM source contract changed; regenerate and review before create preparation')
    proof = json.loads(path.read_text())
    if proof.get('source_id') != SOURCE or proof.get('status') != STATUS:
        raise ValueError('Pinned DOM no-child source qualification is absent or changed')


def bind(result):
    path = ROOT / 'references/fsm-dom-empty-element-contract.json'
    proof = json.loads(path.read_text())
    if proof.get('source_id') != SOURCE or proof.get('status') != STATUS:
        raise ValueError('Pinned DOM no-child source qualification is absent or changed')
    result['sources'][SOURCE] = {
        'path': 'references/fsm-dom-empty-element-contract.json',
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'claim_scope': proof['qualification'],
    }
    found = []
    for key, source in result['sources'].items():
        if key in SERIALIZATIONS or source.get('path') in {
            'references/airfare-create-serialization.json',
            'references/mileage-create-serialization.json',
            'references/miscellaneous-create-serialization.json',
            'references/per-diem-create-serialization.json',
        }:
            source['source_ids'] = list(dict.fromkeys([*source.get('source_ids', []), SOURCE]))
            found.append(key)
    if len(found) != 4:
        raise ValueError('All four expanded create serializations must bind the DOM source proof')
    return result
