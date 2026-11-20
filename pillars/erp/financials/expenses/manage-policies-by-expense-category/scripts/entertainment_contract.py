"""Entertainment contracts bound to their own reviewed evidence, live-pending."""
import hashlib
from entertainment_profile import ROOT,P,R,SOURCE,IDENTITY,INPUTS,LIMITS,BEHAVIORS


def extend(result,catalog):
    proof = ROOT/'references/entertainment-profile.json'
    result['sources'][SOURCE] = {'path':'references/entertainment-profile.json',
        'sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope':'Reviewed Entertainment source/UI and export shape; CSV writes and persistence remain live-pending. No import approval.'}
    ids = [SOURCE]
    audits = {'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    for entity in (P,R):
        parent = entity == P
        managed = {'Status':'DRAFT'}
        if parent:
            managed.update(AttendeeTypesFlag='N',EmpRateDeterminantFlag='N',NonempRateDeterminantFlag='N',
                           EnabledRoleFlag='N',RateLimitTypeCode='ATTENDEE')
        supported = INPUTS|{'CurrencyOptionCode'} if parent else {P+'.PolicyName',*LIMITS,'StartDate','EndDate'}
        updates = INPUTS-{'PolicyName','CurrencyCode','NumOfAttendeesCurrCode'} if parent else set(LIMITS)
        fields = {f:{'create':'supported' if f in supported else 'unsupported',
            'update':'supported' if f in updates else 'unsupported','source_ids':ids[:]} for f in catalog['entities'][entity]}
        for field in managed: fields[field]['create'] = 'consumer-managed'
        for field in audits: fields[field]['create'] = 'system-managed'
        for field in supported:
            if field.endswith('Flag'): fields[field]['value_mapping'] = {'Yes':'Y','No':'N'}
            if field in {'EmpAttendeeAmtCode','NonempAttendeeTypeCode','NonempAttendeeAmtCode','NonempJobTitleCode'}:
                fields[field]['allowed_values'] = sorted(BEHAVIORS)
        if parent:
            fields['PolicyEnforcementCode']['allowed_values'] = ['UPPER','VIOLATION']
            fields['CurrencyOptionCode']['allowed_values'] = ['SINGLE']
            fields['PolicyName'].update(max_length=80,length_unit='characters')
            fields['Description'].update(max_length=240,length_unit='characters')
        else:
            for field in ('StartDate','EndDate'): fields[field]['csv_date_format'] = '%Y/%m/%d'
        required = ['PolicyName','Status','NumOfAttendeesFlag','EmployeeAttendeeInfoFlag','NonEmplAttendeeInfoFlag','EnabledRateLimitFlag'] if parent else [P+'.PolicyName','StartDate','Status']
        entry = {'ready':True,'review_status':'source_reviewed_authoring_extension_live_pending',
            'requires_live_qualification':True,'identity_fields':['PolicyName'] if parent else IDENTITY[:],
            'nullable_identity_fields':[] if parent else [f for f in IDENTITY if f not in {P+'.PolicyName','StartDate'}],
            'identity_match':'exact','operations':['create','update'],
            'required_fields':{'create':required[:],'update':required[:]},'fields':fields,
            'cross_field_rules':[],
            'create_managed_fields':{f:{'value':v,'source_ids':ids[:]} for f,v in managed.items()},
            'create_empty_fields':{f:{'behavior':'system_generated' if f in audits else 'remains_empty','source_ids':ids[:]} for f in fields if f not in managed}}
        for fact in ('ownership','identity','required_fields','operations','cross_field'): entry[fact+'_source_ids'] = ids[:]
        if parent:
            entry['reference_fields'] = ['CurrencyCode','NumOfAttendeesCurrCode']
            # Conditional retained references are resolved by candidate construction,
            # because count mode and rate mode have different currency fields.
            entry['validate_retained_reference_fields'] = []
        else:
            entry['parent'] = {'entity':P,'parent_field':'PolicyName','child_field':P+'.PolicyName','source_ids':ids[:]}
            entry['cross_field_rules'] = [{'kind':'nonnegative_decimal','field':f,'source_ids':ids[:]} for f in LIMITS]
        result['entities'][entity] = entry
    return result
