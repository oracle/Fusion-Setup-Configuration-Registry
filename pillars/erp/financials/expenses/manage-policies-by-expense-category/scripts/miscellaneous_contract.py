"""Source-qualified Misc create preparation and bounded existing-row writes."""
import hashlib

from miscellaneous_profile import (ROOT, P, R, SOURCE, IDENTITY, PARENT_UPDATES,
    RATE_UPDATES, LIMITS, CONTROLS)


def extend(result, catalog):
    proof = ROOT/'references/miscellaneous-source-contract.json'
    result['sources'][SOURCE] = {'path': 'references/miscellaneous-source-contract.json',
        'sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope': 'Own Misc AM/VO/EO/UI graph, keys, raw migration accessors and explicit no-determinant create preparation for LIMIT/PERCENT/BOTH. No live create or target parity qualification.'}
    shared='SHARED-FSM-MISC-CREATE-SERIALIZATION'
    result['sources'][shared]={'path':'references/miscellaneous-create-serialization.json',
        'sha256':hashlib.sha256((ROOT/'references/miscellaneous-create-serialization.json').read_bytes()).hexdigest(),
        'claim_scope':'Pinned CSV/XML/ADF create path joined to own Misc no-determinant graph; managed and deliberate-null values, not inferred business defaults.'}
    ids = [SOURCE,shared]
    audit={'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    for entity in (P, R):
        parent = entity == P
        fields = {f: {'create': 'unresolved', 'update': 'outside_initial_scope', 'source_ids': ids[:]}
            for f in catalog['entities'][entity]}
        for field in PARENT_UPDATES if parent else RATE_UPDATES:
            fields[field].update(update='unresolved', role='business', application_validation={
                'kind': 'field_operation', 'override_eligible': True, 'source_ids': ids[:],
                'uncertainty': 'Pinned shared implementation is located; broader target field-write behavior remains evidence_unresolved outside exact reviewed existing-row cases; no 100-percent cap is established by own percentage attribute metadata.',
                'failure_surface': 'FSM may reject the exact business-field update or persist a different value. Preserve the unresolved warning, native immutable approval, one submission, diagnostics and fresh-export reconciliation; no automatic retry.'})
        if parent:
            fields['PolicyName'].update(max_length=60, length_unit='characters')
            fields['Description'].update(max_length=240, length_unit='characters')
            fields['RateTypeCode']['allowed_values'] = ['LIMIT', 'PERCENT', 'BOTH']
            fields['PolicyEnforcementCode']['allowed_values'] = ['UPPER', 'VIOLATION']
            fields['PeriodMonth']['allowed_values'] = [f'{m:02}' for m in range(1, 13)]
            for field in {*CONTROLS, 'EnabledEligibilityFlag', 'DaysBasedItemParentFlag', *(f+'Flag' for f in LIMITS)}:
                fields[field]['value_mapping'] = {'Yes': 'Y', 'No': 'N'}
            required = ['PolicyName', 'Status', 'RateTypeCode', 'PolicyEnforcementCode']
            rules = [{'kind': 'nonnegative_decimal', 'field': f, 'source_ids': ids[:]}
                for f in ('WarningTolerance', 'ErrorTolerance')]
            rules.append({'kind': 'strict_decimal_order', 'lower': 'WarningTolerance',
                'upper': 'ErrorTolerance', 'source_ids': ids[:]})
        else:
            for field in ('StartDate', 'EndDate'):
                fields[field]['csv_date_format'] = '%Y/%m/%d'
            required = [P+'.PolicyName', 'StartDate', 'Status']
            rules = [{'kind': 'nonnegative_decimal', 'field': f, 'source_ids': ids[:]}
                for f in sorted(RATE_UPDATES)]
        supported=({'PolicyName','CurrencyCode','CurrencyOptionCode',*PARENT_UPDATES}if parent else {P+'.PolicyName','StartDate','EndDate',*RATE_UPDATES})
        managed={'Status':'DRAFT'}
        if parent:managed.update(EnabledRoleFlag='N',EnabledLocationFlag='N',EnabledGenderFlag='N')
        else:managed.update({f:''for f in IDENTITY if f not in {P+'.PolicyName','StartDate','EndDate'}})
        for field in supported:fields[field]['create']='supported'
        for field in managed:fields[field]['create']='consumer-managed'
        for field in audit:fields[field]['create']='system-managed'
        create_required=required+(['EnabledEligibilityFlag',*CONTROLS,*(f+'Flag'for f in LIMITS)]if parent else [])
        entry = {'ready': True, 'review_status': 'source_qualified_create_preparation_live_pending_existing_updates_scoped',
            'planned_operations': ['create', 'update'], 'operations': ['create','update'],
            'identity_fields': ['PolicyName'] if parent else IDENTITY[:],
            'nullable_identity_fields': [] if parent else [f for f in IDENTITY if f not in {P+'.PolicyName', 'StartDate'}],
            'identity_match': 'exact', 'required_fields': {'create':create_required,'update': required}, 'fields': fields,
            'create_managed_fields':{f:{'value':v,'source_ids':ids[:]}for f,v in managed.items()},
            'create_empty_fields':{f:{'behavior':'system_generated'if f in audit else'remains_empty','source_ids':ids[:]}for f in catalog['entities'][entity]if f not in managed or managed[f]==''},
            'cross_field_rules': rules, 'requires_live_qualification': True}
        for fact in ('ownership', 'identity', 'required_fields', 'operations', 'cross_field'):
            entry[fact+'_source_ids'] = ids[:]
        if parent:
            # Applicability is evaluated by the task gate on the merged row;
            # PERCENT has no monetary currency. No mode conversion is inferred.
            entry['reference_fields'] = ['CurrencyCode']
            entry['validate_retained_reference_fields'] = []
        else:
            entry['parent'] = {'entity': P, 'parent_field': 'PolicyName',
                'child_field': P+'.PolicyName', 'source_ids': ids[:]}
        result['entities'][entity] = entry
    return result
