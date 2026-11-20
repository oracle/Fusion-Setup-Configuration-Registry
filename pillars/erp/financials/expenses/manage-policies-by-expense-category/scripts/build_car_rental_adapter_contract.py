"""Synchronize Car Rental's task-owned runtime and public protocol declarations."""
import argparse
import copy
import json
from workbook_intake import ROOT
from car_rental_profile import P,R,SOURCE


def build(descriptor,runtime):
    result=copy.deepcopy(descriptor)
    for entity in result['package']['entities']:
        name=entity['name']
        if name not in {P,R}:continue
        current=runtime['entities'][name]
        ids=[SOURCE]
        entity['keyFields']=current['identity_fields'][:]
        entity['nullableKeyFields']={f:{'sourceIds':ids[:],
            'boundary':'Own Car Rental service AltKey optional coordinate; preserved in the full key.'}
            for f in current['nullable_identity_fields']}
        entity['requiredFields']=current['required_fields']['update'][:]
        entity['updateFields']={}
        entity['createFields']={f:{'sourceIds':current['fields'][f]['source_ids'][:]}
            for f in current['fields']if current['fields'][f].get('create')in{'supported','consumer-managed'}}
        entity['unresolvedUpdateFields']={f:{'boundary':rule['application_validation']['uncertainty'],
            'sourceIds':ids[:],'overrideEligible':True,'overrideBlockers':[]}
            for f,rule in current['fields'].items() if rule.get('update')=='unresolved'}
        for op in ('create','update'):
            target=op in current['operations']
            entity['operationOwnership'][op]={'implementorTarget':target,
                'roles':['implementor-target','reconciliation-target'] if target else ['reconciliation-target'],
                'sourceIds':ids[:],
                'boundary':('Source-qualified SINGLE no-determinant create preparation; explicit managed values, target references and native approval required; live create pending.'
                    if op=='create'else'Own service/EO existing update preparation; unresolved fields require explicit exact-candidate acceptance.')}
        entity['fieldConstraints']={f:{'maxLength':rule['max_length'],'lengthUnit':rule['length_unit'],'sourceIds':ids[:]}
            for f,rule in current['fields'].items() if 'max_length' in rule}
    optional=result['normalization']['designInput'].setdefault('optional',[])
    if 'evidenceUnresolvedUpdateOverrides' not in optional:optional.append('evidenceUnresolvedUpdateOverrides')
    evidence=result['generation']['sourceEvidence']
    line='Car Rental source-qualified SINGLE create preparation and scoped existing updates: references/car-rental-source-contract.json; references/shared-fsm-create-serialization.json; references/field-uncertainty-validation.md'
    if line not in evidence:evidence.append(line)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    path=ROOT/'e2e-adapter.json'
    value=build(json.loads(path.read_text()),json.loads((ROOT/'references/fsm-runtime-contract.json').read_text()))
    if args.write:path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'generated_source_qualified_create_preparation','write':args.write,'create_ready':True,'live_create_qualified':False,'import_approved':False}))


if __name__=='__main__':main()
