"""Build the user-authorized Accommodations extension, without live claims."""
import copy
import hashlib

from accommodations_profile import ROOT, P, R, SOURCE, IDENTITY


def extend(result, catalog):
    proof = ROOT/'references/accommodations-profile.json'
    result['sources'][SOURCE] = {'path':'references/accommodations-profile.json',
        'sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
        'claim_scope':'User-authorized local authoring extension informed by UI and pinned historical source facts; Accommodations CSV acceptance, serialization and target persistence require live reconciliation.'}
    ids = [SOURCE]
    meals = 'ORA_EXM_MEALS_POLICY'
    audit = {'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    for entity, template in [(P,meals),(R,meals+'_LINE')]:
        entry = copy.deepcopy(result['entities'][template])
        # Keep the existing operation-contract shape, while binding every
        # Accommodations fact to its own authoring evidence, never Meals success.
        def rebind(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == 'source_ids' or key.endswith('_source_ids'):
                        value[key] = ids[:]
                    else:
                        rebind(child)
            elif isinstance(value, list):
                for child in value: rebind(child)
        rebind(entry)
        entry['review_status'] = 'user_authorized_authoring_extension_live_pending'
        entry['requires_live_qualification'] = True
        entry['fields'] = {field:copy.deepcopy(entry['fields'].get(field,
            {'create':'unsupported','update':'unsupported','source_ids':ids}))
            for field in catalog['entities'][entity]}
        managed = {'Status':'DRAFT'}
        if entity == P:
            managed.update(EnabledRoleFlag='N',EnabledLocationFlag='N',EnabledSeasonRateFlag='N',EnabledGenderFlag='N')
            entry['identity_fields'] = ['PolicyName']
            entry['nullable_identity_fields'] = []
        else:
            entry['identity_fields'] = IDENTITY[:]
            entry['nullable_identity_fields'] = [f for f in IDENTITY if f not in {P+'.PolicyName','StartDate'}]
            entry['parent'] = {'entity':P,'parent_field':'PolicyName','child_field':P+'.PolicyName','source_ids':ids}
            entry['fields'][P+'.PolicyName'].update(create='supported',source_ids=ids)
            entry['cross_field_rules'] = [{'kind':'nonnegative_decimal','field':'DailyLimit','source_ids':ids}]
        for operation, required in entry['required_fields'].items():
            entry['required_fields'][operation] = [f.replace(meals+'.',P+'.') for f in required
                if f.replace(meals+'.',P+'.') in catalog['entities'][entity]]
            if entity == R:
                entry['required_fields'][operation].append('DailyLimit')
        entry['create_managed_fields'] = {f:{'value':v,'source_ids':ids} for f,v in managed.items()}
        entry['create_empty_fields'] = {f:{'behavior':'system_generated' if f in audit else 'remains_empty',
            'source_ids':ids} for f in catalog['entities'][entity] if f not in managed}
        for field in managed:
            entry['fields'][field].update(create='consumer-managed',source_ids=ids)
        result['entities'][entity] = entry
    return result
