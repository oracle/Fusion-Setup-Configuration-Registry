"""Own Per Diem new-policy create and existing-row update contracts."""
import hashlib
from per_diem_profile import ROOT, P, R, V, SOURCE, IDENTITY, VALUE_IDENTITY, AMOUNTS, STRUCTURAL


def extend(result, catalog):
    proof = ROOT/'references/per-diem-source-contract.json'
    result['sources'][SOURCE] = {'path': 'references/per-diem-source-contract.json',
        'sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope': 'Own P/L/V service graph, keys, accessors and source-qualified new policy groups. Existing updates retain exact acceptance; no native create or automatic UI import-side synchronization claim.'}
    from per_diem_create import CREATE_SOURCE,IDS
    path=ROOT/'references/per-diem-create-serialization.json'
    result['sources'][CREATE_SOURCE]={'path':'references/per-diem-create-serialization.json',
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'claim_scope':'Pinned generic CSV/null/key/ADF reader joined to exact Per Diem graph and explicit managed/derived/value create recipes only; live create pending.'}
    exposed = {s['entity']: {c['csv_field'] for c in s['columns'] if c.get('csv_field')}
        for s in catalog['sheets'] if s['entity'] in {P, R}}
    for entity, identity in ((P, ['PolicyName']), (R, IDENTITY), (V, VALUE_IDENTITY)):
        fields = {f: {'create': 'unresolved', 'update': 'outside_initial_scope', 'source_ids': IDS[:]}
            for f in catalog['entities'][entity]}
        updates = (exposed[P] - STRUCTURAL if entity == P else AMOUNTS if entity == R else {'LineValue'})
        for field in updates:
            fields[field].update(update='unresolved', role='business', application_validation={
                'kind': 'field_operation', 'override_eligible': True, 'source_ids': [SOURCE],
                'uncertainty': 'Pinned shared implementation is located; broader target field-write behavior outside exact reviewed cases remains evidence_unresolved for these existing-row updates.',
                'failure_surface': 'FSM may reject the exact P/L/V update or persist a different resulting state. Exact immutable approval, one submission, native diagnostics and fresh-export reconciliation are required; no automatic retry.'})
        for sheet in catalog['sheets']:
            if sheet['entity'] != entity:
                continue
            for spec in sheet['columns']:
                field = spec.get('csv_field')
                if not field:
                    continue
                if spec.get('boolean'):
                    fields[field]['value_mapping'] = {'Yes': 'Y', 'No': 'N'}
                if spec.get('display_values'):
                    fields[field]['allowed_values'] = sorted(set(spec['display_values'].values()))
        fields['PolicyName' if entity == P else P+'.PolicyName']['max_length'] = 60
        if entity == P:
            fields['Description']['max_length'] = 240
        for rule in fields.values():
            if 'max_length' in rule:
                rule['length_unit'] = 'characters'
        if entity == R:
            for f in ('StartDate', 'EndDate'):
                fields[f]['csv_date_format'] = '%Y/%m/%d'
        audit={'CreatedBy','CreationDate','LastUpdateDate','LastUpdatedBy','LastUpdateLogin'}
        if entity==P:
            from per_diem_profile import DETERMINANTS
            managed={'Status':'DRAFT','PerdiemPolicyType':'GENERIC','CurrencyOptionCode':'SINGLE',**{f:'N'for f in sorted(DETERMINANTS)}}
            derived={'TimeBasedRateModelFlag':{'derivation':'formula_time_prefix','source_ids':IDS[:]}}
            supported=exposed[P]
            create_required=['PolicyName','CurrencyCode','RateFormulaMethodCode','TimeBasedRateModelFlag',
                'AllowRateConversionFlag','RateIncludeMealsFlag','RateIncludeAccomFlag','RateIncludeOtherFlag',
                'MealDeductionFlag','AccomDeductionFlag',*managed]
        elif entity==R:
            managed={};derived={f:{'derivation':('anchor_valid_other_draft'if f=='Status'else'same_kind_preceding_upper'),'source_ids':IDS[:]}
                for f in ['Status','LowerLineHours','LowerLineMinutes']}
            supported=exposed[R];create_required=[P+'.PolicyName','StartDate','TypeOfLineCode','Status']
        else:
            managed={};derived={};supported=set()
            create_required=[P+'.PolicyName','TypeOfLineCode','DeterminantCode']
            for field in [P+'.PolicyName','TypeOfLineCode','DeterminantCode','LineValue']:
                fields[field]['create']='consumer-managed'
        for field in supported:fields[field]['create']='supported'
        for field in managed.keys()|derived.keys():fields[field]['create']='consumer-managed'
        for field in audit:fields[field]['create']='system-managed'
        entry = {'ready': True, 'review_status': 'source_qualified_new_policy_preparation_live_pending_existing_updates_scoped',
            'planned_operations': ['create', 'update'], 'operations': ['create','update'],
            'identity_fields': identity[:], 'identity_match': 'exact',
            'nullable_identity_fields': [] if entity == P else [f for f in identity
                if f not in {P+'.PolicyName', 'StartDate', 'TypeOfLineCode'}],
            'required_fields': {'create':create_required,'update': ['PolicyName', 'PerdiemPolicyType', 'Status',
                'CurrencyOptionCode', 'CurrencyCode', 'RateFormulaMethodCode'] if entity == P else
                [P+'.PolicyName', 'StartDate', 'TypeOfLineCode', 'Status'] if entity == R else
                [P+'.PolicyName', 'TypeOfLineCode']},
            'fields': fields,'create_managed_fields':{f:{'value':value,'source_ids':IDS[:]}for f,value in managed.items()},
            'create_derived_fields':derived,
            'create_empty_fields':{f:{'behavior':'system_generated'if f in audit else'remains_empty','source_ids':IDS[:]}
                for f in catalog['entities'][entity]if f not in managed},
            'cross_field_rules': [], 'requires_live_qualification': True}
        for fact in ('ownership', 'identity', 'required_fields', 'operations', 'cross_field'):
            entry[fact+'_source_ids'] = IDS[:]
        if entity != P:
            entry['parent'] = {'entity': P, 'parent_field': 'PolicyName',
                'child_field': P+'.PolicyName', 'source_ids': [SOURCE]}
        if entity == P:
            entry['reference_fields'] = ['CurrencyCode']
            entry['validate_retained_reference_fields'] = ['CurrencyCode']
        if entity == V:
            entry['internal_existing_value_effects_only'] = True
            entry['internal_new_policy_value_effects_only'] = True
        result['entities'][entity] = entry
    return result
