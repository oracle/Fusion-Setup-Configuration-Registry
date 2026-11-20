"""Synchronize public Per Diem existing-row and internal-value ownership."""
import argparse
import copy
import json
from per_diem_profile import ROOT, P, R, V, SOURCE


def build(descriptor, runtime):
    result = copy.deepcopy(descriptor)
    for entry in result['package']['entities']:
        name = entry['name']
        if name not in {P, R, V}:
            continue
        current = runtime['entities'][name]
        from per_diem_create import IDS
        ids = IDS[:]
        entry['keyFields'] = current['identity_fields'][:]
        entry['nullableKeyFields'] = {f: {'sourceIds': ids[:],
            'boundary': 'Own Per Diem service AltKey optional coordinate, retained exactly; no omitted-key write.'}
            for f in current['nullable_identity_fields']}
        entry['requiredFields'] = current['required_fields']['update'][:]
        entry['updateFields'] = {}
        entry['createFields']=({f:{'sourceIds':rule['source_ids'][:]}
            for f,rule in current['fields'].items()if rule.get('create')in {'supported','consumer-managed'}}if name!=V else{})
        entry['unresolvedUpdateFields'] = {f: {'boundary': rule['application_validation']['uncertainty'],
            'sourceIds': ids[:], 'overrideEligible': True, 'overrideBlockers': []}
            for f, rule in current['fields'].items() if rule.get('update') == 'unresolved'}
        for op in ('create', 'update'):
            allowed = op in current['operations']and(name!=V or op=='update')
            entry['operationOwnership'][op] = {'implementorTarget': allowed,
                'roles': ['implementor-target', 'reconciliation-target'] if allowed else ['reconciliation-target'],
                'sourceIds': ids[:], 'boundary':
                    ('Internal code-based effect only, no independent workbook target; new create is source-owned and never implementorTarget.'if name==V else
                     'Source-qualified wholly new no-determinant policy groups; explicit business/managed/derived values and references; live create pending.'if op=='create'else
                     'Own existing-row update, exact business-field acceptance and complete resulting-state validation required.')}
        entry['fieldConstraints'] = {f: {'maxLength': rule['max_length'],
            'lengthUnit': 'characters', 'sourceIds': ids[:]}
            for f, rule in current['fields'].items()
            if 'max_length' in rule and entry.get('types', {}).get(f) == 'string'}
        # Parent-name proxies have an empty metadata type in the FSM export.
        # Keep that declaration intact; the owning parent/runtime still checks
        # its source-backed name length, without inventing a proxy string type.
    old='Per Diem own P/L/V existing-row contract: references/per-diem-source-contract.json; no inferred new rows or import synchronization'
    result['generation']['sourceEvidence']=[s for s in result['generation']['sourceEvidence']if s!=old]
    item = 'Per Diem own P/L/V source-qualified new policy groups and scoped existing updates: references/per-diem-source-contract.json; references/per-diem-create-serialization.json; no live create or automatic import-side UI synchronization'
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
    print(json.dumps({'status': 'generated_source_qualified_new_policy_preparation', 'write': args.write,
        'admitted_shapes_source_qualified':True,'remaining_shapes_blocked':True,'live_create_qualified':False, 'import_approved': False}))


if __name__ == '__main__':
    main()
