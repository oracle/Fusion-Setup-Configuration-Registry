"""Airfare source-qualified create preparation and bounded existing updates."""
import hashlib
from airfare_profile import ROOT, P, R, SOURCE, IDENTITY, UPDATES


def extend(result, catalog):
    proof = ROOT/'references/airfare-source-contract.json'
    result['sources'][SOURCE] = {'path': 'references/airfare-source-contract.json',
        'sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope': 'Own service/VO/EO, keys, associations, scalar accessors and no-determinant CATCH_ALL create preparation. No target/live create qualification; existing update decisions remain separate.'}
    shared='SHARED-FSM-AIRFARE-CREATE-SERIALIZATION'
    path=ROOT/'references/airfare-create-serialization.json'
    result['sources'][shared]={'path':'references/airfare-create-serialization.json',
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'claim_scope':'Pinned generic CSV/XML/ADF implementation joined to the reviewed no-determinant Airfare graph only; no live qualification.'}
    ids = [SOURCE,shared]
    audit={'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    for entity in (P, R):
        parent = entity == P
        fields = {f: {'create': 'unresolved', 'update': 'outside_initial_scope', 'source_ids': ids[:]}
            for f in catalog['entities'][entity]}
        for field in UPDATES if parent else {'FlightClassCode'}:
            fields[field].update(update='unresolved', role='business', application_validation={
                'kind': 'field_operation', 'override_eligible': True, 'source_ids': ids[:],
                'uncertainty': 'The pinned shared implementation is located; broader target field-write behavior remains evidence_unresolved outside exact reviewed existing-row cases.',
                'failure_surface': 'FSM may reject the exact field update or export a different result. Native immutable approval, one submission, diagnostics and fresh-export reconciliation are required; no automatic retry.'})
        if parent:
            fields['PolicyName'].update(max_length=60, length_unit='characters')
            fields['Description'].update(max_length=240, length_unit='characters')
            fields['PolicyEnforcementCode']['allowed_values'] = ['PREVENT', 'VIOLATION']
            fields['DispWarningToUserFlag']['value_mapping'] = {'Yes': 'Y', 'No': 'N'}
            required = ['PolicyName', 'Status', 'EnabledFlightTypeFlag', 'EnabledFlightDurationFlag',
                'EnabledRoleFlag', 'PolicyEnforcementCode']
        else:
            fields['FlightClassCode']['allowed_values'] = ['ANY', 'BUSINESS', 'COACH']
            for f in ('StartDate', 'EndDate'):
                fields[f]['csv_date_format'] = '%Y/%m/%d'
            required = [P+'.PolicyName', 'StartDate', 'TypeOfRateCode', 'Status', 'FlightClassCode']
        supported={'PolicyName','Description','PolicyEnforcementCode','DispWarningToUserFlag'} if parent else {P+'.PolicyName','StartDate','EndDate','FlightClassCode'}
        managed={'Status':'DRAFT'}
        if parent:managed.update(EnabledRoleFlag='N',EnabledFlightTypeFlag='N',EnabledFlightDurationFlag='N')
        else:managed['TypeOfRateCode']='CATCH_ALL'
        for field in supported:fields[field]['create']='supported'
        for field in managed:fields[field]['create']='consumer-managed'
        for field in audit:fields[field]['create']='system-managed'
        entry = {'ready': True, 'review_status': 'source_qualified_create_preparation_live_pending_updates_require_exact_field_acceptance',
            'planned_operations': ['create', 'update'], 'operations': ['create','update'],
            'identity_fields': ['PolicyName'] if parent else IDENTITY[:],
            'nullable_identity_fields': [] if parent else [f for f in IDENTITY if f not in {P+'.PolicyName', 'StartDate', 'TypeOfRateCode'}],
            'identity_match': 'exact', 'required_fields': {'create':required+(['DispWarningToUserFlag'] if parent else []),'update': required}, 'fields': fields,
            'create_managed_fields':{field:{'value':value,'source_ids':ids[:]}for field,value in managed.items()},
            'create_empty_fields':{field:{'behavior':'system_generated'if field in audit else'remains_empty','source_ids':ids[:]}for field in catalog['entities'][entity]if field not in managed},
            'cross_field_rules': [], 'requires_live_qualification': True}
        for fact in ('ownership', 'identity', 'required_fields', 'operations', 'cross_field'):
            entry[fact+'_source_ids'] = ids[:]
        if not parent:
            entry['parent'] = {'entity': P, 'parent_field': 'PolicyName', 'child_field': P+'.PolicyName', 'source_ids': ids[:]}
        result['entities'][entity] = entry
    return result
