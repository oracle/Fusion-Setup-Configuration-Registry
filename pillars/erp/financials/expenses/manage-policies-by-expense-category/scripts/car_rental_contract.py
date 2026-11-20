"""Car Rental create preparation and bounded unresolved existing-field updates."""
import hashlib
from pathlib import Path
from car_rental_profile import ROOT,P,R,SOURCE,IDENTITY,PARENT_INPUTS,UPDATES,CONTROLS


def extend(result,catalog):
    proof=ROOT/'references/car-rental-source-contract.json'
    result['sources'][SOURCE]={'path':'references/car-rental-source-contract.json',
        'sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope':'Own service/EO ownership, full alternate keys, mappings and resulting-state rules; SINGLE no-determinant create preparation joins the pinned shared serialization evidence. No live create qualification.'}
    shared='SHARED-FSM-CREATE-SERIALIZATION'
    shared_path=ROOT/'references/shared-fsm-create-serialization.json'
    result['sources'][shared]={'path':'references/shared-fsm-create-serialization.json',
        'sha256':hashlib.sha256(shared_path.read_bytes()).hexdigest(),
        'claim_scope':'Pinned generic CSV/null/key/create implementation joined only to the reviewed Car Rental graph; no live create or other-category admission.'}
    ids=[SOURCE,shared]
    audit={'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    for entity in (P,R):
        parent=entity==P
        fields={f:{'create':'unresolved','update':'outside_initial_scope','source_ids':ids[:]} for f in catalog['entities'][entity]}
        eligible=UPDATES if parent else {'DailyLimit'}
        for f in eligible:
            fields[f].update(update='unresolved',role='business',application_validation={
                'kind':'field_operation','override_eligible':True,'source_ids':ids[:],
                'uncertainty':'The pinned shared helper and ADF XML implementation are located; broader target field-write behavior remains evidence_unresolved outside the exact reviewed existing-row cases.',
                'failure_surface':'FSM may reject this field update or export a different result. Submit once only after native approval, retain diagnostics, and reconcile a fresh export before completion.'})
        if parent:
            for f in CONTROLS:fields[f]['value_mapping']={'Yes':'Y','No':'N'}
            fields['PolicyName'].update(max_length=60,length_unit='characters')
            fields['Description'].update(max_length=240,length_unit='characters')
            fields['PolicyEnforcementCode']['allowed_values']=['UPPER','VIOLATION']
            required=['PolicyName','Status','CurrencyOptionCode','CurrencyCode','EnabledRoleFlag','EnabledLocationFlag',
                'PolicyEnforcementCode',*CONTROLS]
            rules=[{'kind':'nonnegative_decimal','field':f,'source_ids':ids[:]} for f in ('WarningTolerance','ErrorTolerance')]
            rules.append({'kind':'strict_decimal_order','lower':'WarningTolerance','upper':'ErrorTolerance','source_ids':ids[:]})
        else:
            for f in ('StartDate','EndDate'):fields[f]['csv_date_format']='%Y/%m/%d'
            required=[P+'.PolicyName','StartDate','Status','DailyLimit']
            rules=[{'kind':'nonnegative_decimal','field':'DailyLimit','source_ids':ids[:]}]
        supported=PARENT_INPUTS|{'CurrencyOptionCode'} if parent else {P+'.PolicyName','StartDate','EndDate','DailyLimit'}
        managed={'Status':'DRAFT'}
        if parent:managed.update(EnabledRoleFlag='N',EnabledLocationFlag='N')
        for field in supported:fields[field]['create']='supported'
        for field in managed:fields[field]['create']='consumer-managed'
        for field in audit:fields[field]['create']='system-managed'
        entry={'ready':True,'review_status':'source_qualified_create_preparation_live_pending_updates_require_exact_field_acceptance',
            'planned_operations':['create','update'],'operations':['create','update'],
            'identity_fields':['PolicyName'] if parent else IDENTITY[:],
            'nullable_identity_fields':[] if parent else [f for f in IDENTITY if f not in {P+'.PolicyName','StartDate'}],
            'identity_match':'exact','required_fields':{'create':required[:],'update':required},'fields':fields,
            'create_managed_fields':{f:{'value':v,'source_ids':ids[:]}for f,v in managed.items()},
            'create_empty_fields':{f:{'behavior':'system_generated'if f in audit else'remains_empty',
                'source_ids':ids[:]}for f in catalog['entities'][entity]if f not in managed},
            'cross_field_rules':rules,'reference_fields':['CurrencyCode'] if parent else [],
            'validate_retained_reference_fields':['CurrencyCode'] if parent else [],
            'requires_live_qualification':True}
        for fact in ('ownership','identity','required_fields','operations','cross_field'):entry[fact+'_source_ids']=ids[:]
        if not parent:entry['parent']={'entity':P,'parent_field':'PolicyName','child_field':P+'.PolicyName','source_ids':ids[:]}
        result['entities'][entity]=entry
    return result
