"""Synchronize Miscellaneous's own bounded create/update declarations."""
import argparse
import copy
import json

from miscellaneous_profile import ROOT, P, R, SOURCE


def build(descriptor, runtime):
    result = copy.deepcopy(descriptor)
    for entry in result['package']['entities']:
        name = entry['name']
        if name not in {P, R}:
            continue
        current = runtime['entities'][name]
        ids = [SOURCE,'SHARED-FSM-MISC-CREATE-SERIALIZATION']
        entry['keyFields'] = current['identity_fields'][:]
        entry['nullableKeyFields'] = {f: {'sourceIds': ids[:],
            'boundary': 'Own Misc service alternate-key optional coordinate; preserve exact existing serialization including GenderCode.'}
            for f in current['nullable_identity_fields']}
        entry['requiredFields'] = current['required_fields']['update'][:]
        entry['createFields'] = {f:{'sourceIds':rule['source_ids'][:]}
            for f,rule in current['fields'].items()if rule.get('create')in {'supported','consumer-managed'}}
        entry['updateFields'] = {}
        entry['unresolvedUpdateFields'] = {f: {'boundary': rule['application_validation']['uncertainty'],
            'sourceIds': ids[:], 'overrideEligible': True, 'overrideBlockers': []}
            for f, rule in current['fields'].items() if rule.get('update') == 'unresolved'}
        for op in ('create', 'update'):
            target = op in current['operations']
            entry['operationOwnership'][op] = {'implementorTarget': target,
                'roles': ['implementor-target', 'reconciliation-target'] if target else ['reconciliation-target'],
                'sourceIds': ids[:], 'boundary':
                    'Source-qualified no-determinant LIMIT/PERCENT/BOTH create preparation; explicit business choices, managed/empty fields and target references required; live create pending.'
                    if op=='create'else'Own Misc existing-row preparation; full resulting-state checks and exact unresolved business-field acceptance remain mandatory.'}
        entry['fieldConstraints'] = {f: {'maxLength': rule['max_length'],
            'lengthUnit': rule['length_unit'], 'sourceIds': ids[:]}
            for f, rule in current['fields'].items() if 'max_length' in rule}
    old='Miscellaneous own service/EO/AM/UI existing-row preparation: references/miscellaneous-source-contract.json; no inferred create, 100-percent cap or shared-helper qualification'
    result['generation']['sourceEvidence']=[s for s in result['generation']['sourceEvidence']if s!=old]
    item = 'Miscellaneous no-determinant source-qualified LIMIT/PERCENT/BOTH create preparation and scoped existing updates: references/miscellaneous-source-contract.json; references/miscellaneous-create-serialization.json; live create pending; no invented 100-percent cap'
    if item not in result['generation']['sourceEvidence']:
        result['generation']['sourceEvidence'].append(item)
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
