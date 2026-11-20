"""Mileage source-qualified no-determinant create and scoped existing updates."""
import hashlib
from mileage_profile import ROOT,P,R,SOURCE,IDENTITY,UPDATES

def extend(result,catalog):
    path=ROOT/'references/mileage-source-contract.json'
    result['sources'][SOURCE]={'path':'references/mileage-source-contract.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'claim_scope':'Own service/VO/EO mappings and complete keys joined to the bounded pinned DOM proof for local create preparation. No target/live create qualification; existing update decisions retained.'}
    shared='MILEAGE-CREATE-SERIALIZATION'
    proof=ROOT/'references/mileage-create-serialization.json'
    result['sources'][shared]={'path':'references/mileage-create-serialization.json','sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope':'Pinned CSV/XML/ADF join to own Mileage graph and bounded default Oracle provider/no-child DOM identity proof. No target-build parity or live create admission.'}
    ids=[SOURCE,shared]
    audit={'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    company_path=ROOT/'references/mileage-company-lookup-contract.json'
    company_source='MILEAGE-COMPANY-LOOKUP-SOURCE-CONTRACT'
    result['sources'][company_source]={'path':'references/mileage-company-lookup-contract.json',
        'sha256':hashlib.sha256(company_path.read_bytes()).hexdigest(),
        'claim_scope':'Source-matched read-only exact parent-type/all-consumed-child-code receipt route; no target capture, field-write or import qualification.'}
    for entity in (P,R):
        parent=entity==P
        fields={f:{'create':'unresolved','update':'outside_initial_scope','source_ids':ids[:]} for f in catalog['entities'][entity]}
        for field in UPDATES if parent else {'Rate'}:
            fields[field].update(update='unresolved',role='business',application_validation={
                'kind':'field_operation','override_eligible':True,'source_ids':ids[:],
                'uncertainty':'Pinned shared XML implementation is located; broader target existing-row field-write behavior remains evidence_unresolved outside exact reviewed live cases.',
                'failure_surface':'FSM may reject the exact update or persist different values. Require immutable native approval, one submission, diagnostics and fresh-export reconciliation; no automatic retry.'})
        if parent:
            fields['AdditionalRatesListCode']['source_ids'].append(company_source)
            fields['PolicyName'].update(max_length=60,length_unit='characters');fields['Description'].update(max_length=240,length_unit='characters')
            from mileage_profile import FLAGS
            for f in FLAGS:fields[f]['value_mapping']={'Yes':'Y','No':'N'}
            fields['UnitOfMeasureCode']['allowed_values']=['MILE','KILOMETER','SWEDISH_MILE']
            fields['CommuteDistanceRequiredFlag']['allowed_values']=['ORA_EXM_OPTIONAL','ORA_EXM_REQUIRED']
            fields['PassengerRuleCode']['allowed_values']=['SINGLE','RANGE']
            required=['PolicyName','Status','CurrencyOptionCode','CurrencyCode','UnitOfMeasureCode','CommuteDistanceRequiredFlag']
        else:
            fields['AdditionalRateCode']['source_ids'].append(company_source)
            for f in ('StartDate','EndDate'):fields[f]['csv_date_format']='%Y/%m/%d'
            required=[P+'.PolicyName','StartDate','TypeOfRateCode','Status','Rate']
        from mileage_profile import FLAGS,DETERMINANTS
        supported=({'PolicyName','Description','CurrencyOptionCode','CurrencyCode',*UPDATES} if parent else
            {P+'.PolicyName','StartDate','EndDate','TypeOfRateCode','Rate','CalculationMethodCode','PassengerThreshold','AdditionalRateCode'})
        managed={'Status':'DRAFT'}
        if parent:managed.update({field:'N'for field in DETERMINANTS})
        for field in supported:fields[field]['create']='supported'
        for field in managed:fields[field]['create']='consumer-managed'
        for field in audit:fields[field]['create']='system-managed'
        if not parent:fields['TypeOfRateCode']['allowed_values']=['MILEAGE','PASSENGER','ADDITIONAL']
        create_required=required+list(FLAGS) if parent else required[:]
        entry={'ready':True,'review_status':'source_qualified_create_preparation_live_pending_existing_updates_scoped','planned_operations':['create','update'],
            'operations':['create','update'],
            'identity_fields':['PolicyName'] if parent else list(IDENTITY),
            'nullable_identity_fields':[] if parent else [f for f in IDENTITY if f not in {P+'.PolicyName','StartDate','TypeOfRateCode'}],
            'identity_match':'exact','required_fields':{'create':create_required,'update':required},'fields':fields,'cross_field_rules':[],
            'create_managed_fields':{field:{'value':value,'source_ids':ids[:]}for field,value in managed.items()},
            'create_empty_fields':{field:{'behavior':'system_generated'if field in audit else'remains_empty','source_ids':fields[field]['source_ids'][:]}
                for field in catalog['entities'][entity]if field not in set(managed)|set(create_required)},
            'requires_live_qualification':True}
        for fact in ('ownership','identity','required_fields','operations','cross_field'):entry[fact+'_source_ids']=ids[:]
        if parent:
            entry['reference_fields']=['CurrencyCode'];entry['validate_retained_reference_fields']=['CurrencyCode']
            entry['create_inactive_encodings']={'CommuteDistanceRequiredFlag':{
                'when':{'EnabledDeductCommuteFlag':'N'},'value':'ORA_EXM_OPTIONAL',
                'requires_blank_input':True,'source_ids':ids[:]}}
        else:entry['parent']={'entity':P,'parent_field':'PolicyName','child_field':P+'.PolicyName','source_ids':ids[:]}
        result['entities'][entity]=entry
    return result
