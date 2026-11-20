"""Recompute lookup eligibility from operation-bound, read-only evidence.

These checks qualify selected values, not FSM field write acceptance. Capture
uses the workflow-selected core REST client; this module performs no network I/O.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit

from currency_receipt import digest, origin
from environment_identity import same_binding

MODULE = '47110F64AC0608E2E040449823C60DB6'
ROUTE = 'expense-policy-lookup-core-client-v1'
RESOURCE = '/fscmRestApi/resources/11.13.18.05/standardLookups'
COUNTRY_RESOURCE = '/fscmRestApi/resources/11.13.18.05/territoriesLOV'


def load_receipt_index(path):
    """Read an offline entity/policy/operation/field receipt index.

    Paths are absolute so working-directory changes cannot select other evidence.
    Each field uses either one legacy receipt path or a literal code-to-path
    map when different rows consume different values. Every selected receipt
    remains independently bound and verified at candidate preparation.
    """
    source = Path(path)
    if not source.is_absolute() or source.is_symlink() or not source.is_file():
        raise ValueError('Lookup receipt index must be an absolute regular file')
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate lookup receipt index key')
            result[key] = value
        return result
    value = json.loads(source.read_text(), object_pairs_hook=unique_keys)
    def receipt_path(node):
        if not isinstance(node,str):raise ValueError('Lookup receipt path must be a string')
        receipt=Path(node)
        if not receipt.is_absolute()or receipt.is_symlink()or not receipt.is_file():
            raise ValueError('Lookup receipt must be an absolute regular file')
    def visit(node, depth):
        if depth == 4:
            if isinstance(node,dict):
                if not node:raise ValueError('Lookup code receipt map must not be empty')
                for code,path in node.items():
                    if not isinstance(code,str)or not code or code.strip()!=code:
                        raise ValueError('Lookup receipt codes must be nonblank exact names')
                    receipt_path(path)
            else:receipt_path(node)
            return
        if not isinstance(node, dict):
            raise ValueError('Lookup index requires entity/policy/operation/field mappings')
        for key, child in node.items():
            if not isinstance(key, str) or not key or key.strip() != key:
                raise ValueError('Lookup index keys must be nonblank exact names')
            if depth == 2 and key not in {'create', 'update'}:
                raise ValueError('Lookup index operation must be create or update')
            visit(child, depth + 1)
    visit(value, 0)
    return value


def receipt_for_code(fields,field,code):
    """Select exactly one literal code; never fall back to another value."""
    if not isinstance(fields,dict)or field not in fields:return None
    value=fields[field]
    selected=value.get(code)if isinstance(value,dict)else value
    if selected is not None and not isinstance(selected,(str,Path)):
        raise ValueError('Lookup receipt must be a path or exact code-to-path map')
    return selected


def receipt_paths(index):
    """Inventory every receipt, including unconsumed codes, for immutable binding."""
    for policies in index.values():
        for operations in policies.values():
            for fields in operations.values():
                for value in fields.values():
                    yield from value.values()if isinstance(value,dict)else(value,)


def complete(page):
    if (not isinstance(page, dict) or not isinstance(page.get('items'), list)
            or page.get('hasMore') is not False or page.get('offset', 0) != 0
            or page.get('count', len(page['items'])) != len(page['items'])):
        raise ValueError('Lookup evidence requires a complete, unambiguous response')
    if any(not isinstance(row, dict) for row in page['items']):
        raise ValueError('Malformed lookup row')
    return page['items']


def unique(rows, **keys):
    matches = [r for r in rows if all(r.get(k) == v for k,v in keys.items())]
    if len(matches) != 1:
        raise ValueError('Lookup selection is missing or ambiguous')
    return matches[0]


def returned_child(row, name, target_origin):
    # REST framework versions 6+ place item links under @context. Preserve
    # legacy item links too; never guess an endpoint from a key or self URL.
    links=[]
    if 'links' in row:
        if not isinstance(row['links'],list):raise ValueError('Malformed returned lookup links')
        links.extend(row['links'])
    if '@context' in row:
        context=row['@context']
        if not isinstance(context,dict):raise ValueError('Malformed returned lookup context')
        if 'links' in context:
            if not isinstance(context['links'],list):raise ValueError('Malformed returned lookup context links')
            links.extend(context['links'])
    links = [r.get('href') for r in links
             if isinstance(r, dict) and r.get('rel') == 'child' and r.get('name') == name]
    if len(links) != 1 or not isinstance(links[0], str):
        raise ValueError('Missing or ambiguous returned lookup child link')
    u = urlsplit(links[0]); target = urlsplit(origin(target_origin))
    if (u.scheme != 'https' or u.hostname != target.hostname or (u.port or 443) != (target.port or 443)
            or u.username or u.password or u.query or u.fragment
            or not u.path.startswith(RESOURCE + '/') or not u.path.endswith('/child/' + name)
            or any(p in {'.','..'} for p in u.path.split('/'))):
        raise ValueError('Unsafe or cross-environment lookup child link')
    return u.path


def classify_standard(parent_page, codes_page, context_page, lookup_type, code):
    parent = unique(complete(parent_page), LookupType=lookup_type)
    if parent.get('ModuleId') != MODULE:
        raise ValueError('Lookup is outside the Expenses module')
    selected = unique(complete(codes_page), LookupCode=code)
    if selected.get('EnabledFlag') != 'Y':
        raise ValueError('Lookup code is not enabled')
    if lookup_type == 'EXM_TICKET_CLASS' and code == 'FIRST':
        raise ValueError('First is excluded by TicketClassLOVVO')
    context = unique(complete(context_page), LookupType=lookup_type, LookupCode=code)
    app, reference_set = context.get('ViewApplicationId'), context.get('SetId')
    # Framework 9 serializes high-precision numeric attributes as strings,
    # including these small IDs. Admit only the same exact canonical values.
    if isinstance(app,str) and app in {'0','10016'}:app=int(app)
    if isinstance(reference_set,str) and reference_set=='0':reference_set=0
    if type(app) is not int or app not in {0,10016} or type(reference_set) is not int or reference_set != 0:
        raise ValueError('Lookup application or reference-set context is not qualified')
    return {'lookup_type':lookup_type,'code':code,'view_application_id':app,'set_id':reference_set,
            'reference_resolved':True,'boundary':'Enabled UI lookup value only; no FSM acceptance or import approval'}


def classify_country(page, code):
    selected = unique(complete(page), TerritoryCode=code)
    if selected.get('EnabledFlag') != 'Y':
        raise ValueError('Country is not enabled')
    return {'code':code,'reference_resolved':True}


def response(receipt_path, capture, request):
    if not isinstance(capture, dict) or capture.get('request') != request or capture.get('http_status') != 200:
        raise ValueError('Lookup request or HTTP status differs from the declared read-only request')
    member = capture.get('response_file')
    if not isinstance(member,str) or member in {'','.','..'} or Path(member).name != member or '\\' in member:
        raise ValueError('Unsafe lookup evidence file')
    p = receipt_path.parent / member
    if p.is_symlink() or digest(p) != capture.get('response_sha256'):
        raise ValueError('Lookup evidence changed')
    return json.loads(p.read_text())


def receipt_identity(receipt_path, expected_binding, selection):
    """Validate a host-recorded receipt for one exact field and operation.

    selection contains entity, policy_name, operation, field, lookup_type, code.
    expected_binding uses currency_receipt.binding and includes the current
    intake catalog hash. Research snapshots cannot stand in for these receipts.
    """
    if not isinstance(selection, dict) or set(selection) != {'entity','policy_name','operation','field','lookup_type','code'}:
        raise ValueError('Exact lookup selection required')
    if any(not isinstance(v,str) or not v or v.strip()!=v for v in selection.values()):
        raise ValueError('Exact nonblank selection values required')
    if not isinstance(expected_binding,dict):
        raise ValueError('Expected lookup binding required')
    path = Path(receipt_path)
    if path.is_symlink():
        raise ValueError('Lookup receipt must not be a symlink')
    receipt = json.loads(path.read_text())
    if (receipt.get('schema_version') != '1.0' or receipt.get('route') != ROUTE or receipt.get('status') != 'captured'
            or not same_binding(receipt.get('binding'), expected_binding) or receipt.get('adapter_sha256') != digest(__file__)
            or receipt.get('selection') != selection or selection.get('operation') not in {'create','update'}):
        raise ValueError('Lookup receipt identity or operation binding mismatch')
    from workbook_intake import load_catalog
    catalog = load_catalog()
    if expected_binding.get('intake_catalog_sha256') != digest(Path(__file__).resolve().parents[1]/'references/intake-fields.json'):
        raise ValueError('Lookup field mapping changed')
    fields = [c for s in catalog['sheets'] if s['entity']==selection.get('entity')
              for c in s['columns'] if c.get('csv_field')==selection.get('field')]
    if len(fields)!=1 or fields[0].get('lookup')!=selection.get('lookup_type'):
        raise ValueError('Lookup type does not belong to the selected field')
    return path, receipt


def verify_standard(receipt_path, expected_binding, selection):
    path, receipt = receipt_identity(receipt_path, expected_binding, selection)
    typ, code = selection['lookup_type'], selection['code']
    if not all(isinstance(x,str) and x and x.strip()==x for x in (typ,code)):
        raise ValueError('Exact nonblank lookup type and code required')
    parent = response(path,receipt.get('parent'),{'method':'GET','path':RESOURCE,
        'query':{'finder':'LookupTypeFinder;LookupType='+typ,'limit':'100'}})
    p = unique(complete(parent),LookupType=typ)
    codes = response(path,receipt.get('codes'),{'method':'GET','path':returned_child(p,'lookupCodes',expected_binding['origin']),
        'query':{'limit':'500'}})
    c = unique(complete(codes),LookupCode=code)
    context = response(path,receipt.get('context'),{'method':'GET','path':returned_child(c,'lookupsDFF',expected_binding['origin']),
        'query':{'limit':'100'}})
    return classify_standard(parent,codes,context,typ,code)


def verify_country(receipt_path, expected_binding, selection):
    path, receipt = receipt_identity(receipt_path, expected_binding, selection)
    if selection['lookup_type'] != 'enabled_territory':
        raise ValueError('Country receipt requires the territory resolver')
    page = response(path,receipt.get('country'),{'method':'GET','path':COUNTRY_RESOURCE,
        'query':{'finder':'TerritoryCodeAllRowsFinder;TerritoryCode='+selection['code'],'limit':'100'}})
    return classify_country(page,selection['code'])


def verify_selection(receipt_path, expected_binding, selection):
    """Dispatch only implemented resolvers; no availability or dropdown waiver."""
    typ = selection.get('lookup_type') if isinstance(selection,dict) else None
    if typ == 'enabled_territory':
        result = verify_country(receipt_path,expected_binding,selection)
    elif isinstance(typ,str) and typ.startswith(('EXM_','ORA_EXM_')):
        result = verify_standard(receipt_path,expected_binding,selection)
    else:
        raise ValueError('Selected lookup requires its separately qualified resolver')
    return {'selection':selection,'receipt_sha256':digest(receipt_path),'classification':result,
            'boundary':'Captured reference eligibility only; no field write acceptance or import approval'}


def verify_retained_parent(entity, values, receipt_index, expected_binding, *, company_context=None):
    """Verify an unchanged parent included as rate context before serialization."""
    from category_scope import owning_policy
    if owning_policy(entity)!=entity or not values.get('PolicyName'):
        raise ValueError('Retained lookup context requires an exact owning policy')
    name=values['PolicyName']
    receipts=None if receipt_index is None else receipt_index.get(entity,{}).get(name,{}).get('update')
    return verify_resulting_fields(entity,name,'update',values,receipts,expected_binding,
        company_context=company_context)


def verify_resulting_fields(entity, policy_name, operation, values, receipts, expected_binding,
        *, company_context=None, company_receipt=None):
    """Check encoded resulting values, including retained lookup selections.

    Currency and annual month checks remain owned by their existing validators.
    Every other catalog lookup must resolve through this gate; dynamic resolver
    gaps remain explicit rather than silently accepting the workbook dropdown.
    receipts maps fields to one path or a literal code-to-path map. A code map
    adds no eligibility/availability waiver and cannot reuse another code.
    """
    from workbook_intake import load_catalog
    from expanded_category_intake import ENTITIES
    if entity not in ENTITIES:
        return []
    reviews=[]
    for sheet in load_catalog()['sheets']:
        if sheet['entity'] != entity:
            continue
        for spec in sheet['columns']:
            field, typ = spec.get('csv_field'), spec.get('lookup')
            if not typ or typ == 'enabled_active_currency' or not values.get(field):
                continue
            if typ == 'MONTH':
                from datetime import date
                month = values[field]
                active = values.get('YearlyLimitFlag') == 'Y'
                if not active:
                    reviews.append({'entity': entity, 'policy_name': policy_name,
                        'operation': operation, 'field': field, 'lookup_type': 'MONTH',
                        'code': month, 'period_day': values.get('PeriodDay'),
                        'status': 'INACTIVE_PRESERVED', 'validation_scope': 'inactive_annual_reset',
                        'target_eligibility_verified': False,
                        'boundary': 'Retained inactive values are preserved without normalization. Parent profile controls proposed inactive writes; no target eligibility or FSM write qualification.'})
                    continue
                if not str(month).isdigit() or not 1 <= int(month) <= 12:
                    raise ValueError(entity+'.'+field+': invalid local numeric month domain')
                day = values.get('PeriodDay')
                if day not in (None, ''):
                    if not str(day).isdigit():
                        raise ValueError(entity+'.PeriodDay: invalid local calendar day')
                    try:
                        date(2001, int(month), int(day))
                    except ValueError as error:
                        raise ValueError(entity+': invalid local annual month/day pair') from error
                reviews.append({'entity': entity, 'policy_name': policy_name,
                    'operation': operation, 'field': field, 'lookup_type': 'MONTH',
                    'code': month, 'period_day': day, 'status': 'PASS',
                    'validation_scope': 'active_local_numeric_month_and_present_day',
                    'target_eligibility_verified': False,
                    'boundary': 'Task calendar/domain check only. FND MONTH binding is source observed; all target lookup codes and FSM serialization/write behavior remain unqualified. Parent profile owns conditional required-day checks.'})
                continue
            if typ in {'expenses_user_extensible_lookup_type','selected_company_lookup_code'}:
                from mileage_company_lookup import P,R,FIELD,TYPE,CHILD_TYPE,verify
                if entity==P and field==FIELD and typ==TYPE:
                    if values.get('EnabledAdditnlRatesFlag')!='Y':
                        continue  # Inactive retained list is not newly selected.
                    selected=receipt_for_code(receipts,field,values[field])
                    if (company_context is None or company_context.get('policy_name')!=policy_name
                            or company_context.get('operation')!=operation
                            or company_context.get('lookup_type')!=values[field] or selected is None):
                        raise ValueError('Mileage company list requires exact complete consuming context and operation-bound parent receipt')
                elif entity==R and field=='AdditionalRateCode' and typ==CHILD_TYPE:
                    selected=company_receipt
                    if (company_context is None or company_context.get('policy_name')!=policy_name
                            or company_context.get('operation')!=operation
                            or values.get('TypeOfRateCode')!='ADDITIONAL'
                            or values[field] not in company_context.get('child_codes',[]) or selected is None):
                        raise ValueError('Mileage company rate requires the consuming parent list/code receipt, never an arbitrary lookup type')
                else:
                    raise ValueError('Dynamic lookup is not owned by this exact Mileage field')
                reviews.append(verify(selected,expected_binding,company_context))
                continue
            if not isinstance(receipts,dict) or field not in receipts or expected_binding is None:
                raise ValueError(entity+'.'+str(field)+': operation-bound lookup evidence required')
            selected=receipt_for_code(receipts,field,values[field])
            if selected is None:
                raise ValueError(entity+'.'+str(field)+': operation-bound lookup evidence required for exact code '+str(values[field]))
            reviews.append(verify_selection(selected,expected_binding,{
                'entity':entity,'policy_name':policy_name,'operation':operation,
                'field':field,'lookup_type':typ,'code':values[field]}))
    return reviews
