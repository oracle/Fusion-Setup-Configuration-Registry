"""Maintain the ordinary accepted Meals runtime; no network or import.

Only Meals authoring contracts are retained. Run --dry-run to inspect the selected
contract; --write updates the generated runtime JSON after authoring review.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from accepted_meals_profile import ROOT, P, R, PROFILE, definition
from workbook_intake import load_catalog


def build(original):
    result = copy.deepcopy(original)
    result['status'] = 'ready_for_single_currency_meals_with_expanded_input_validation'
    result['executable_profile'] = PROFILE
    source = 'LIVE-ACCEPTED-MEALS-PROFILE'
    ids = [source]
    result['sources'][source] = {'path':'references/accepted-meals-profile.json',
        'sha256':hashlib.sha256((ROOT/'references/accepted-meals-profile.json').read_bytes()).hexdigest(),
        'evidence':definition()['evidence'],
        'claim_scope':'Accepted core observations plus user-authorized expanded inputs and batch capability. Expanded combinations and effective-dated batches remain pending live reconciliation. No import approval.',
        'batch_extension':definition()['batch_extension']}
    result['sources']['MEALS-EXPANDED-INPUTS'] = {
        'path':'references/accepted-meals-profile.json',
        'sha256':result['sources'][source]['sha256'],
        'source_ids':['EO-MealsPolicy','EO-MealsPolLine','SEED-EXM-YES-NO','UI-MealsPolicy-Boolean'],
        'claim_scope':'Local input acceptance and cross-field validation; not a new live outcome or general helper qualification.'}
    result['package'] = {'strategy':'sparse_selected_rows','unsubmitted_rows':'preserve','source_ids':ids}
    catalog = load_catalog()
    audit = {'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
    parent_inputs = {'PolicyName','Description','SingleInstanceLimitFlag','DailyLimitFlag','CurrencyCode',
        'PolicyEnforcementCode','PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag',
        'CurrencyOptionCode','WarningTolerance','ErrorTolerance'}
    domains = definition()['parent_settings']
    for entity in (P,R):
        fields = {f:{'create':'unsupported','update':'unsupported','source_ids':ids} for f in catalog['entities'][entity]}
        boolean_proof = json.loads((ROOT/'references/boolean-encoding-evidence.json').read_text())
        for field, proof in boolean_proof['fields'].get(entity,{}).items():
            if field in fields:
                fields[field]['source_ids'] = [*proof['source_ids'],source]
        supported = parent_inputs if entity == P else {P+'.PolicyName','SingleInstanceLimit','DailyLimit','StartDate','EndDate'}
        for field in supported:
            fields[field]['create'] = 'supported'
        updates = (parent_inputs-{'PolicyName','CurrencyCode','CurrencyOptionCode'}) if entity == P else {'SingleInstanceLimit','DailyLimit'}
        for field in updates:
            fields[field]['update'] = 'supported'
        for field in supported:
            fields[field]['source_ids'] = list(dict.fromkeys([*fields[field]['source_ids'],'MEALS-EXPANDED-INPUTS']))
        for field, rule in fields.items():
            if entity == P and field in domains:
                rule['allowed_values'] = [domains[field]]
            if entity == P and field in definition()['parent_domains']:
                rule['allowed_values'] = definition()['parent_domains'][field]
            if field.endswith('Flag') and field in parent_inputs:
                rule['value_mapping'] = {'Yes':'Y','No':'N'}
        if entity == P:
            for field, maximum in [('PolicyName',80),('Description',240)]:
                fields[field].update(max_length=maximum,length_unit='characters')
        else:
            fields['StartDate']['source_ids'] = ['LIVE-SELECTED-RATE-STARTDATE-ENCODING',source]
            fields['StartDate']['csv_date_format'] = '%Y/%m/%d'
            fields['EndDate']['source_ids'] = ['EO-MealsPolLine',source]
            fields['EndDate']['csv_date_format'] = '%Y/%m/%d'
        managed = {'Status':'DRAFT'}
        if entity == P:
            managed.update(EnabledRoleFlag='N',EnabledLocationFlag='N')
        for field in managed:
            fields[field]['create'] = 'consumer-managed'
        for field in audit:
            fields[field]['create'] = 'system-managed'
        required = (['PolicyName','CurrencyCode','CurrencyOptionCode','Status','SingleInstanceLimitFlag',
            'DailyLimitFlag','PolicyEnforcementCode','PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag']
            if entity == P else [P+'.PolicyName','StartDate','Status'])
        entry = {'ready':True,'review_status':'accepted_core_source_validated_expansion_live_pending',
            'identity_fields':['PolicyName'] if entity == P else
                [P+'.PolicyName','CurrencyCode','EndDate','GeoLocName','RoleName','StartDate','TypeOfRateCode','ZoneCode'],
            'nullable_identity_fields':[] if entity == P else
                ['CurrencyCode','EndDate','GeoLocName','RoleName','TypeOfRateCode','ZoneCode'],
            'identity_match':'exact','operations':['create','update'],
            'required_fields':{'create':required,'update':required},
            'fields':fields,'cross_field_rules':[],
            'create_managed_fields':{f:{'value':v,'source_ids':ids} for f,v in managed.items()},
            'create_empty_fields':{f:{'behavior':'system_generated' if f in audit else 'remains_empty','source_ids':ids}
                for f in catalog['entities'][entity] if f not in managed}}
        for fact in ('ownership','identity','required_fields','operations','cross_field'):
            entry[fact+'_source_ids'] = ids
        if entity == P:
            entry['reference_fields'] = ['CurrencyCode']
            entry['validate_retained_reference_fields'] = ['CurrencyCode']
            numeric_ids = ['EO-MealsPolicy','MEALS-EXPANDED-INPUTS']
            entry['cross_field_rules'] = [
                {'kind':'nonnegative_decimal','field':'WarningTolerance','source_ids':numeric_ids},
                {'kind':'nonnegative_decimal','field':'ErrorTolerance','source_ids':numeric_ids},
                {'kind':'strict_decimal_order','lower':'WarningTolerance','upper':'ErrorTolerance','source_ids':numeric_ids}]
            for field in ('RateIncludeMealsFlag','RateIncludeOtherFlag'):
                entry['create_empty_fields'][field] = {'behavior':'observed_server_normalization',
                    'expected_export_value':'N','source_ids':ids}
        else:
            entry['parent'] = {'entity':P,'parent_field':'PolicyName','child_field':P+'.PolicyName','source_ids':ids}
            entry['cross_field_rules'] = [{'kind':'nonnegative_decimal','field':field,'source_ids':ids}
                for field in ['SingleInstanceLimit','DailyLimit']]
        result['entities'][entity] = entry
    result['entities'] = {entity: result['entities'][entity] for entity in (P,R)}
    result.pop('period_entity', None)
    result.pop('blocked_reason', None)
    date_source = result['sources']['LIVE-SELECTED-RATE-STARTDATE-ENCODING']
    date_source['sha256'] = hashlib.sha256((ROOT/'references/date-encoding-evidence.json').read_bytes()).hexdigest()
    # Preserve the transitive source chain for the supported contracts, not the
    # retired categories. Full export schemas remain in the input catalog.
    used = set()
    def visit(value):
        if isinstance(value, dict):
            for child in value.values(): visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
        elif isinstance(value, str) and value in result['sources']:
            used.add(value)
    visit(result['entities'])
    visit(result['package'])
    while True:
        count = len(used)
        for key in list(used): visit(result['sources'][key])
        if len(used) == count: break
    result['sources'] = {key: value for key, value in result['sources'].items() if key in used}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run',action='store_true')
    mode.add_argument('--write',action='store_true')
    args = parser.parse_args()
    path = ROOT/'references/fsm-runtime-contract.json'
    result = build(json.loads(path.read_text()))
    if args.write:
        path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'profile':PROFILE,
        'ready_entities':[e for e,c in result['entities'].items() if c.get('ready')],
        'write':args.write,'import_approved':False}))


if __name__ == '__main__':
    main()
