"""Source-bound company lookup bundles for Mileage create/update consumers.

One parent-field receipt covers the exact resulting list and every retained/proposed
ADDITIONAL code consumed by that policy. No caller-chosen unbound lookup type,
new reference values, source defaults, authentication or mutation permission.
"""
import json
import re
from pathlib import Path

from currency_receipt import digest
import policy_lookup_preflight as lookup

P = 'ORA_EXM_MILEAGE_POLICY'
R = 'ORA_EXM_MILEAGE_LINE'
FIELD = 'AdditionalRatesListCode'
TYPE = 'expenses_user_extensible_lookup_type'
CHILD_TYPE = 'selected_company_lookup_code'
ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT/'references/mileage-company-lookup-contract.json'


def validate_evidence(contract):
    if contract.get('sources', {}).get('MILEAGE-COMPANY-LOOKUP-SOURCE-CONTRACT', {}).get('sha256') != digest(PROOF):
        raise ValueError('Mileage company lookup source contract changed; regenerate and review the runtime contract')


def context(parent, rates, policy_name, operation='update'):
    """Derive all consuming codes from actual resolved rows, never caller input."""
    if operation not in {'create','update'} or parent.get('PolicyName') != policy_name or parent.get('EnabledAdditnlRatesFlag') != 'Y':
        raise ValueError('Mileage company lookup requires its exact enabled parent and consuming operation context')
    typ = parent.get(FIELD)
    # Finder syntax is not a string-escaping API. Fail closed on unsafe tokens.
    if not isinstance(typ, str) or re.fullmatch(r'[A-Za-z0-9_]{1,30}', typ) is None:
        raise ValueError('Mileage selected company lookup type requires an exact safe source-sized code')
    selected = [r for r in rates if r.get(P+'.PolicyName', '').casefold() == policy_name.casefold()]
    if any(r.get(P+'.PolicyName') != policy_name for r in selected):
        raise ValueError('Case-only Mileage company policy association collision')
    codes = [r.get('AdditionalRateCode') for r in selected if r.get('TypeOfRateCode') == 'ADDITIONAL']
    if not codes or any(not isinstance(c, str) or not c or c.strip() != c or len(c) > 30 for c in codes):
        raise ValueError('Mileage company lookup requires actual consuming ADDITIONAL child codes')
    return {'entity': P, 'policy_name': policy_name, 'operation': operation,
        'parent_field': FIELD, 'lookup_type': typ, 'child_codes': sorted(set(codes))}


def workbook_rates(records, baseline_rates, policy_name):
    """Union retained codes with exact proposed rate inputs, never sample codes."""
    from workbook_intake import load_catalog
    sheet=next(s for s in load_catalog()['sheets']if s['entity']==R)
    mappings={s['csv_field']:s.get('display_values',{})for s in sheet['columns']if s['csv_field']}
    result=[dict(row)for row in baseline_rates]
    for record in records:
        if record['entity']!=R or record['policy_name'].casefold()!=policy_name.casefold():continue
        if record['policy_name']!=policy_name:raise ValueError('Case-only Mileage company proposed association collision')
        values={field:mappings.get(field,{}).get(value,value)for field,value in record['values'].items()}
        result.append(values)
    return result


def consuming_operations(records, rows, policy_name):
    """Bind capture operation to an actual full-key workbook consumer."""
    from workbook_intake import load_catalog
    from datetime import date
    from mileage_rate_profile import IDENTITY
    mappings={(s['entity'],c['csv_field']):c.get('display_values',{})for s in load_catalog()['sheets']for c in s['columns']if c['csv_field']}
    operations=set()
    for record in records:
        if record['entity']not in {P,R} or record['policy_name']!=policy_name:continue
        entity=record['entity'];values={field:mappings.get((entity,field),{}).get(value,value)for field,value in record['values'].items()}
        if entity==P:
            matches=[r for r in rows.get(P,[])if r.get('PolicyName')==policy_name]
        else:
            for field in ('StartDate','EndDate'):
                if values.get(field):
                    parsed=date.fromisoformat(values[field])
                    if parsed.isoformat()!=values[field]:raise ValueError('Mileage lookup consumer date is not normalized ISO input')
                    values[field]=parsed.strftime('%Y/%m/%d')
            matches=[r for r in rows.get(R,[])if all(r.get(field,'')==values.get(field,'')for field in IDENTITY)]
        if len(matches)>1:raise ValueError('Mileage company capture has ambiguous full-key consumer')
        operations.add('update'if matches else'create')
    return operations


def from_workbook(model, rows, selection):
    """Validate a capture's parent choice against workbook plus exact baseline."""
    name = selection.get('policy_name')
    if (selection.get('entity') != P or selection.get('field') != FIELD
            or selection.get('lookup_type') != TYPE or selection.get('operation') not in {'create','update'}):
        raise ValueError('Capture Mileage company codes through the consuming parent AdditionalRatesListCode field')
    parents = [r for r in rows.get(P, []) if r.get('PolicyName', '').casefold() == str(name).casefold()]
    if len(parents)>1 or parents and parents[0]['PolicyName'] != name:
        raise ValueError('Mileage company capture requires an exact unambiguous baseline parent')
    from category_scope import owning_policy
    consuming = [r for r in model['records'] if owning_policy(r['entity']) == P and r['policy_name'] == name]
    if not consuming:
        raise ValueError('Mileage company lookup has no consuming workbook policy or rate')
    patch = [r['values'] for r in consuming if r['entity'] == P]
    if len(patch) > 1:
        raise ValueError('Mileage company capture has ambiguous parent input')
    if not parents and len(patch)!=1:raise ValueError('Mileage company create capture requires its exact proposed parent')
    if selection['operation']not in consuming_operations(consuming,rows,name):
        raise ValueError('Mileage company capture operation has no exact workbook consumer')
    parent = {**(parents[0]if parents else{}), **(patch[0] if patch else {})}
    if parent.get('EnabledAdditnlRatesFlag') in {'Yes', 'No'}:
        parent['EnabledAdditnlRatesFlag'] = {'Yes': 'Y', 'No': 'N'}[parent['EnabledAdditnlRatesFlag']]
    result = context(parent, workbook_rates(consuming,rows.get(R, []),name), name, selection['operation'])
    if selection.get('code') != result['lookup_type']:
        raise ValueError('Mileage company lookup type differs from the resulting workbook/baseline parent choice')
    return result


def selection_for(ctx):
    return {'entity': P, 'policy_name': ctx['policy_name'], 'operation': ctx['operation'],
        'field': FIELD, 'lookup_type': TYPE, 'code': ctx['lookup_type']}


def check_context(ctx):
    if (not isinstance(ctx, dict) or set(ctx) != {'entity','policy_name','operation','parent_field','lookup_type','child_codes'}
            or ctx.get('entity') != P or ctx.get('operation') not in {'create','update'} or ctx.get('parent_field') != FIELD
            or not isinstance(ctx.get('policy_name'), str) or not ctx['policy_name'].strip()
            or not isinstance(ctx.get('lookup_type'), str) or re.fullmatch(r'[A-Za-z0-9_]{1,30}', ctx['lookup_type']) is None
            or not isinstance(ctx.get('child_codes'), list) or not ctx['child_codes']
            or any(not isinstance(c, str) or not c or c.strip() != c or len(c) > 30 for c in ctx['child_codes'])
            or ctx['child_codes'] != sorted(set(ctx['child_codes']))):
        raise ValueError('Exact resolved Mileage company consuming context is required')


def complete(page):
    rows = lookup.complete(page)
    if type(page.get('count')) is not int or type(page.get('offset')) is not int:
        raise ValueError('Mileage company lookup requires explicit complete count/offset metadata')
    return rows


def parent_item(page, typ):
    rows = complete(page)
    if len(rows) != 1:
        raise ValueError('Mileage company lookup type finder must return exactly one parent')
    selected = lookup.unique(rows, LookupType=typ)
    if selected.get('ModuleId') != lookup.MODULE or selected.get('CustomizationLevel') not in {'U', 'E'}:
        raise ValueError('Mileage company lookup type must belong to Expenses and have U/E customization level')
    return selected


def child_context(page, typ, code):
    rows = complete(page)
    if len(rows) != 1:
        raise ValueError('Mileage company child context must be exact and unambiguous')
    selected = lookup.unique(rows, LookupType=typ, LookupCode=code)
    app, reference_set = selected.get('ViewApplicationId'), selected.get('SetId')
    if isinstance(app, str) and app in {'0', '10016'}: app = int(app)
    if isinstance(reference_set, str) and re.fullmatch(r'0|-?[1-9][0-9]*', reference_set): reference_set = int(reference_set)
    if (type(app) is not int or app not in {0, 10016} or type(reference_set) is not int
            or not -(2**63) <= reference_set < 2**63):
        raise ValueError('Mileage company code application/set identity is missing or outside the source context')
    # EXM_LOOKUP_VALUES filters application but not a fixed SetId. Do not borrow
    # the static resolver's SetId0 restriction or discard ambiguous contexts.
    return {'code': code, 'view_application_id': app, 'set_id': reference_set}


def verify(path, binding, expected_context):
    check_context(expected_context)
    selection = selection_for(expected_context)
    path, receipt = lookup.receipt_identity(path, binding, selection)
    if (receipt.get('company_context') != expected_context or receipt.get('company_adapter_sha256') != digest(__file__)
            or receipt.get('company_source_sha256') != digest(PROOF)):
        raise ValueError('Mileage company receipt context or source binding changed')
    typ = expected_context['lookup_type']
    page = lookup.response(path, receipt.get('parent'), {'method':'GET','path':lookup.RESOURCE,
        'query':{'finder':'LookupTypeFinder;LookupType='+typ,'limit':'100'}})
    parent = parent_item(page, typ)
    codes = lookup.response(path, receipt.get('codes'), {'method':'GET',
        'path':lookup.returned_child(parent, 'lookupCodes', binding['origin']), 'query':{'limit':'500'}})
    items = complete(codes)
    captures = receipt.get('company_code_contexts')
    if not isinstance(captures, dict) or set(captures) != set(expected_context['child_codes']):
        raise ValueError('Mileage company receipt must cover exactly every consumed child code')
    reviews = []
    for code in expected_context['child_codes']:
        item = lookup.unique(items, LookupCode=code)
        if item.get('EnabledFlag') != 'Y':
            raise ValueError('Mileage company code is not enabled')
        page = lookup.response(path, captures[code], {'method':'GET',
            'path':lookup.returned_child(item, 'lookupsDFF', binding['origin']), 'query':{'limit':'100'}})
        reviews.append(child_context(page, typ, code))
    return {'company_context': expected_context, 'customization_level': parent['CustomizationLevel'],
        'codes': reviews, 'receipt_sha256': digest(path), 'reference_resolved': True,
        'boundary': 'Source-matched target eligibility for the exact consuming Mileage list/codes only; field writes and imports remain separately governed.'}


def capture(selection, binding, directory, get, ctx):
    """GET-only capture through the existing selected core-client callback."""
    check_context(ctx)
    if selection != selection_for(ctx):
        raise ValueError('Mileage company capture selection differs from the consuming parent context')
    directory = Path(directory)
    if directory.exists() or directory.is_symlink():
        raise ValueError('Lookup capture output must be a new directory')
    directory.mkdir(parents=True)
    path = directory/'receipt.json'
    receipt = {'schema_version':'1.0','route':lookup.ROUTE,'status':'captured',
        'selection': selection, 'binding': binding, 'adapter_sha256': digest(lookup.__file__),
        'company_context': ctx, 'company_adapter_sha256': digest(__file__),
        'company_source_sha256': digest(PROOF), 'company_code_contexts': {}}
    path.write_text(json.dumps(receipt, indent=2)+'\n')
    try:
        lookup.receipt_identity(path, binding, selection)
        def read(name, endpoint, query):
            request = {'method':'GET','path':endpoint,'query':query}
            response = directory/(name+'.json')
            status = get(request, response)
            item = {'request':request,'http_status':status,'response_file':response.name,'response_sha256':digest(response)}
            return item, lookup.response(path, item, request)
        typ = ctx['lookup_type']
        receipt['parent'], page = read('parent', lookup.RESOURCE, {'finder':'LookupTypeFinder;LookupType='+typ,'limit':'100'})
        parent = parent_item(page, typ)
        receipt['codes'], page = read('codes', lookup.returned_child(parent, 'lookupCodes', binding['origin']), {'limit':'500'})
        items = complete(page)
        for index, code in enumerate(ctx['child_codes']):
            item = lookup.unique(items, LookupCode=code)
            if item.get('EnabledFlag') != 'Y': raise ValueError('Mileage company code is not enabled')
            captured, page = read('context-'+str(index), lookup.returned_child(item, 'lookupsDFF', binding['origin']), {'limit':'100'})
            receipt['company_code_contexts'][code] = captured
            child_context(page, typ, code)
        path.write_text(json.dumps(receipt, indent=2)+'\n')
        return verify(path, binding, ctx)
    except Exception:
        receipt['status'] = 'failed'
        path.write_text(json.dumps(receipt, indent=2)+'\n')
        raise
