"""Source-owned inactive Mileage encoding, never an active business default."""
import json
from mileage_profile import ROOT,P,SOURCE,validate_evidence

FIELD='CommuteDistanceRequiredFlag'
VALUE='ORA_EXM_OPTIONAL'
SOURCE_IDS=[SOURCE,'MILEAGE-CREATE-SERIALIZATION']


def create_values(entity,operation,supplied,current,contract):
    if entity!=P or operation!='create' or supplied.get('EnabledDeductCommuteFlag')!='N':
        return {},[]
    if supplied.get(FIELD)not in ('',None):
        raise ValueError('Mileage inactive commute mode must be blank in the workbook; no hidden input or clearing')
    expected={'when':{'EnabledDeductCommuteFlag':'N'},'value':VALUE,
        'requires_blank_input':True,'source_ids':SOURCE_IDS}
    if current.get('create_inactive_encodings',{}).get(FIELD)!=expected:
        raise ValueError('Mileage inactive create encoding is outside the exact reviewed source recipe')
    validate_evidence(contract)
    if current.get('fields',{}).get(FIELD,{}).get('create')!='supported':
        raise ValueError('Mileage commute field create ownership is not reviewed')
    return {FIELD:VALUE},[{'field':FIELD,'value':VALUE,'source_ids':SOURCE_IDS,
        'condition':'explicit EnabledDeductCommuteFlag=N and blank inactive workbook cell',
        'ownership':'consumer-owned inactive package encoding; no active business choice or EO default inferred'}]


def capture_inactive_selection(model,baseline_rows,selection):
    """Allow only the exact derived reference consumed by a new parent."""
    if (selection.get('entity')!=P or selection.get('field')!=FIELD
            or selection.get('operation')!='create'):
        return None
    name=selection.get('policy_name')
    if baseline_rows is None:raise ValueError('Mileage derived capture needs the exact baseline identity context')
    if any(row.get('PolicyName','').casefold()==str(name).casefold()for row in baseline_rows.get(P,[])):
        return None  # An existing parent never acquires create defaults here.
    matches=[r for r in model['records']if r['entity']==P and r['policy_name']==name]
    if len(matches)!=1:return None
    values=dict(matches[0]['values'])
    values['EnabledDeductCommuteFlag']={'Yes':'Y','No':'N'}.get(values.get('EnabledDeductCommuteFlag'),values.get('EnabledDeductCommuteFlag'))
    if values['EnabledDeductCommuteFlag']!='N':return None
    runtime=json.loads((ROOT/'references/fsm-runtime-contract.json').read_text())
    current=runtime['entities'][P]
    if 'create'not in current.get('operations',[]):raise ValueError('Mileage create operation is not admitted for derived capture')
    derived,review=create_values(P,'create',values,current,runtime)
    if selection.get('code')!=derived.get(FIELD):raise ValueError('Mileage derived lookup selection differs from the inactive source encoding')
    return {'value_source':'source_owned_inactive_create_encoding','derived_create_review':review,
        'operation_boundary':'New exact parent with explicit No only; target eligibility and native execution remain separate'}
