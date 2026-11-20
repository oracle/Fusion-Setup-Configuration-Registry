"""Synchronize Airfare's bounded create and existing update declarations."""
import argparse
import copy
import json
from airfare_profile import ROOT, P, R, SOURCE


def build(descriptor, runtime):
    result = copy.deepcopy(descriptor)
    for entry in result['package']['entities']:
        name = entry['name']
        if name not in {P, R}:
            continue
        current = runtime['entities'][name]
        ids = [SOURCE,'SHARED-FSM-AIRFARE-CREATE-SERIALIZATION']
        entry['keyFields'] = current['identity_fields'][:]
        entry['nullableKeyFields'] = {f: {'sourceIds': ids[:],
            'boundary': 'Own Airfare service AltKey optional coordinate; preserve in the complete existing key.'}
            for f in current['nullable_identity_fields']}
        entry['requiredFields'] = current['required_fields']['update'][:]
        entry['updateFields'] = {}
        entry['createFields']={f:{'sourceIds':rule['source_ids'][:]}
            for f,rule in current['fields'].items()if rule.get('create')in {'supported','consumer-managed'}}
        entry['unresolvedUpdateFields'] = {f: {'boundary': rule['application_validation']['uncertainty'],
            'sourceIds': ids[:], 'overrideEligible': True, 'overrideBlockers': []}
            for f, rule in current['fields'].items() if rule.get('update') == 'unresolved'}
        for op in ('create', 'update'):
            target = op in current['operations']
            entry['operationOwnership'][op] = {'implementorTarget': target,
                'roles': ['implementor-target', 'reconciliation-target'] if target else ['reconciliation-target'],
                'sourceIds': ids[:], 'boundary':
                    'Source-qualified no-determinant CATCH_ALL create preparation; explicit business choices, managed values and target references required; live create pending.'
                    if op=='create' else 'Own service existing-row preparation; exact unresolved business-field acceptance required.'}
        entry['fieldConstraints'] = {f: {'maxLength': rule['max_length'],
            'lengthUnit': rule['length_unit'], 'sourceIds': ids[:]}
            for f, rule in current['fields'].items() if 'max_length' in rule}
    evidence = result['generation']['sourceEvidence']
    old='Airfare own service/EO existing-row preparation: references/airfare-source-contract.json; no inferred create or shared-helper qualification'
    evidence[:]=[line for line in evidence if line!=old]
    item = 'Airfare no-determinant CATCH_ALL source-qualified create preparation and scoped updates: references/airfare-source-contract.json; references/airfare-create-serialization.json; live create pending'
    if item not in evidence:
        evidence.append(item)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    path = ROOT/'e2e-adapter.json'
    value = build(json.loads(path.read_text()), json.loads((ROOT/'references/fsm-runtime-contract.json').read_text()))
    if args.write:
        path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': 'generated_source_qualified_create_preparation', 'write': args.write,
        'create_ready': True, 'live_create_qualified':False, 'import_approved': False}))


if __name__ == '__main__':
    main()
