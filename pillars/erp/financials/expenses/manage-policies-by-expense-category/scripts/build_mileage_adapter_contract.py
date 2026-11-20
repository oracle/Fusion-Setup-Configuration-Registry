"""Project Mileage source-owned runtime facts into the public descriptor.

PassengerThreshold remains int; the installed public reader must support the
explicit source-backed nullable-int key before this descriptor can execute.
"""
import argparse
import copy
import json
from mileage_profile import ROOT,P,R,SOURCE

def build(descriptor,runtime):
    result=copy.deepcopy(descriptor)
    for entry in result['package']['entities']:
        if entry['name'] not in {P,R}:continue
        current=runtime['entities'][entry['name']];ids=[SOURCE,'MILEAGE-CREATE-SERIALIZATION']
        entry['keyFields']=current['identity_fields'][:]
        entry['nullableKeyFields']={f:{'sourceIds':ids[:],'boundary':'Own Mileage service alternate-key optional coordinate; retain the complete existing key and source type.'} for f in current['nullable_identity_fields']}
        entry['requiredFields']=current['required_fields']['update'][:];entry['updateFields']={}
        entry['createFields']={field:{'sourceIds':rule['source_ids'][:]}
            for field,rule in current['fields'].items()if rule.get('create')in {'supported','consumer-managed'}}
        entry['unresolvedUpdateFields']={f:{'boundary':r['application_validation']['uncertainty'],'sourceIds':ids[:],
            'overrideEligible':True,'overrideBlockers':[]} for f,r in current['fields'].items() if r.get('update')=='unresolved'}
        for op in ('create','update'):
            target=op in current['operations'];entry['operationOwnership'][op]={'implementorTarget':target,
                'roles':['implementor-target','reconciliation-target'] if target else ['reconciliation-target'],
                'sourceIds':ids[:],'boundary':('Source-qualified no-determinant create preparation with the bounded pinned default Oracle provider/no-child DOM proof. Explicit choices, complete keys and operation-bound references required; target parity and live create remain pending.' if op=='create'else'Own Mileage existing-row preparation; exact business-field uncertainty acceptance required.')}
        entry['fieldConstraints']={f:{'maxLength':r['max_length'],'lengthUnit':r['length_unit'],'sourceIds':ids[:]} for f,r in current['fields'].items() if 'max_length' in r}
    old='Mileage own service/EO existing-row preparation: references/mileage-source-contract.json; no inferred create/shared-helper qualification'
    previous='Mileage no-determinant source-qualified create preparation and scoped existing updates: references/mileage-source-contract.json; references/mileage-create-serialization.json; live create pending'
    result['generation']['sourceEvidence']=[line for line in result['generation']['sourceEvidence']if line not in {old,previous}]
    text='Mileage no-determinant source-qualified create preparation: references/mileage-source-contract.json; references/mileage-create-serialization.json; references/fsm-dom-empty-element-contract.json; no target/live qualification'
    if text not in result['generation']['sourceEvidence']:result['generation']['sourceEvidence'].append(text)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    path=ROOT/'e2e-adapter.json';value=build(json.loads(path.read_text()),json.loads((ROOT/'references/fsm-runtime-contract.json').read_text()))
    if args.write:path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'generated_source_qualified_create_preparation','write':args.write,'local_create_ready':True,'live_create_qualified':False,'import_approved':False}))
