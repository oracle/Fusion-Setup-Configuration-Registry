"""Capture one operation-bound reference via the workflow-selected core client.

No import, authentication fallback or automatic retry. The caller supplies the
validated consuming selection and binding; resulting-state verification checks
them independently before a candidate can use the receipt.
"""
import argparse
import importlib
import json
from pathlib import Path
import socket
import ssl
import subprocess
import sys
from urllib.error import URLError

from currency_receipt import digest, origin
from environment_identity import same_environment
import policy_lookup_preflight as lookup


class LookupTransportError(ValueError):
    def __init__(self,failure_class,message,**diagnostic):
        self.failure_class=failure_class
        self.diagnostic=diagnostic
        super().__init__(message)


def transport_diagnostic(error):
    """Classify core exception causes without disclosing raw URLs or headers."""
    pending, seen = [error], set()
    while pending and len(seen) < 20:
        item = pending.pop(0)
        if not isinstance(item,BaseException) or id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item,socket.gaierror):
            return {'transport_reason':'dns_resolution',
                'recommended_action':'The target hostname could not be resolved. Check VPN/DNS and sandbox network access. If resolution works only outside the sandbox, request an authorized execution context for the same declared capture command; do not change the endpoint, client or lookup checks. No automatic retry.'}
        if isinstance(item,ssl.SSLCertVerificationError):
            return {'transport_reason':'tls_certificate',
                'recommended_action':'Repair the approved network certificate trust. Do not disable TLS verification or retry automatically.'}
        if isinstance(item,TimeoutError):
            return {'transport_reason':'timeout',
                'recommended_action':'Check target/network availability before explicitly retrying this read-only capture in a new output directory. No automatic retry.'}
        if isinstance(item,PermissionError):
            return {'transport_reason':'network_permission',
                'recommended_action':'Check execution-context network permissions and obtain the required authorization before another attempt. No automatic retry.'}
        pending.extend([item.__cause__,item.__context__])
        if isinstance(item,URLError):
            pending.append(item.reason)
    return {'transport_reason':'unclassified_transport',
        'recommended_action':'Diagnose the approved target/network and execution context before another attempt. Raw transport details are suppressed; no automatic retry or substitute client.'}


def selection_spec(selection):
    """Require an exact consuming field before interpreting its input label."""
    from workbook_intake import load_catalog
    if (not isinstance(selection,dict) or set(selection)!={'entity','policy_name','operation','field','lookup_type','code'}
            or any(not isinstance(v,str) or not v or v.strip()!=v for v in selection.values())
            or selection['operation'] not in {'create','update'}):
        raise ValueError('Exact consuming lookup selection required')
    specs=[c for s in load_catalog()['sheets'] if s['entity']==selection['entity']
        for c in s['columns'] if c.get('csv_field')==selection['field']]
    if len(specs)!=1 or specs[0].get('lookup')!=selection['lookup_type']:
        raise ValueError('Lookup selection differs from the task field mapping')
    return specs[0]


def encoded_selection(selection, runtime=None):
    """Use the ordinary import encoder, never a global Yes/No replacement.

    Explicit CSV codes remain exact. Display labels are accepted only through
    this field's declared intake mapping and runtime serialization contract.
    """
    from workbook_intake import ROOT, normalize
    from build_fsm_from_workbook import field_value
    spec=selection_spec(selection)
    if runtime is None:
        runtime=json.loads((ROOT/'references/fsm-runtime-contract.json').read_text())
    rule=runtime.get('entities',{}).get(selection['entity'],{}).get('fields',{}).get(selection['field'])
    if not isinstance(rule,dict):
        raise ValueError('Lookup selection requires its import field encoding contract')
    code=selection['code']
    if spec.get('boolean'):
        encoded={field_value(label,rule,spec) for label in ('Yes','No')}
        if code not in encoded:
            code=field_value(normalize(code,spec),rule,spec)
    else:
        code=field_value(normalize(code,spec),rule,spec)
    return {**selection,'code':code}


def supplied_selection(workbook,selection,baseline_rows=None):
    """Bind capture to a supplied cell or an exact retained parent field.

    The caller-declared create/update value is checked again against the actual
    baseline operation by candidate preparation. Reference capture grants no
    operation or field-write acceptance.
    """
    from workbook_intake import read_workbook,load_catalog
    model=read_workbook(workbook)
    if model['status']!='local_shape_valid':
        raise ValueError('Correct workbook input before lookup capture')
    spec=selection_spec(selection)
    typ=selection['lookup_type']
    if typ in {'expenses_user_extensible_lookup_type','selected_company_lookup_code'}:
        from mileage_company_lookup import from_workbook
        if baseline_rows is None:
            raise ValueError('Mileage company capture requires its exact baseline consuming context')
        ctx=from_workbook(model,baseline_rows,selection)
        return {'value_source':'resolved_workbook_baseline_parent_and_existing_children',
            'company_context':ctx,'operation_boundary':'Read-only exact consuming list/code eligibility; no write or import approval'}
    if typ!='enabled_territory' and not typ.startswith(('EXM_','ORA_EXM_')):
        raise ValueError('Selected lookup requires a separately qualified capture route')
    if selection['entity']=='ORA_EXM_MILEAGE_POLICY'and selection['field']=='CommuteDistanceRequiredFlag':
        from mileage_create_values import capture_inactive_selection
        derived=capture_inactive_selection(model,baseline_rows,selection)
        if derived is not None:return derived
    values=[r['values'][selection['field']] for r in model['records']
        if r['entity']==selection['entity'] and r['policy_name']==selection['policy_name']
        and selection['field'] in r['values']]
    if spec.get('boolean'):
        values=[encoded_selection({**selection,'code':value})['code'] for value in values]
    if not values and baseline_rows is not None:
        from category_scope import owning_policy
        entity,name=selection['entity'],selection['policy_name']
        if entity.endswith('_LINE') or selection['operation']!='update':
            raise ValueError('Retained lookup capture requires an existing parent update context')
        consuming=[r for r in model['records']
            if owning_policy(r['entity'])==entity and r['policy_name']==name]
        if not consuming:
            raise ValueError('Retained lookup has no consuming workbook policy or rate')
        parents=[r for r in baseline_rows.get(entity,[]) if r.get('PolicyName','').casefold()==name.casefold()]
        if len(parents)!=1 or parents[0].get('PolicyName')!=name:
            raise ValueError('Retained lookup parent must resolve to one exact baseline identity')
        if not parents[0].get(selection['field']) or parents[0][selection['field']]!=selection['code']:
            raise ValueError('Retained lookup must equal the exact nonempty baseline value')
        return {'matched_retained_values':1,'consuming_workbook_rows':len(consuming),
            'value_source':'verified_baseline_parent','operation_boundary':
            'Retained parent context only; candidate preparation independently verifies resulting values and operation'}
    matches = [value for value in values if value == selection['code']]
    if not matches:
        raise ValueError('Lookup selection must equal the exact supplied workbook value')
    return {'matched_supplied_values':len(matches),'operation_boundary':
        'Caller-declared operation; exact baseline operation is independently checked during candidate preparation'}


def capture(selection, binding, directory, get, *, company_context=None):
    """Capture a fresh receipt using a supplied read-only core-client adapter.

    get(request, response_path) must persist a response and return HTTP status.
    This function performs no retries and never accepts partial responses.
    """
    if not isinstance(selection,dict):
        raise ValueError('Exact consuming lookup selection required')
    if selection.get('lookup_type') in {'expenses_user_extensible_lookup_type','selected_company_lookup_code'}:
        from mileage_company_lookup import capture as capture_company
        return capture_company(selection,binding,directory,get,company_context)
    if company_context is not None:
        raise ValueError('Company context cannot be attached to another lookup route')
    directory = Path(directory)
    if directory.exists() or directory.is_symlink():
        raise ValueError('Lookup capture output must be a new directory')
    directory.mkdir(parents=True)
    receipt = {'schema_version':'1.0','route':lookup.ROUTE,'status':'captured',
        'selection':selection,'binding':binding,'adapter_sha256':digest(lookup.__file__)}
    path = directory/'receipt.json'
    # Validate the exact field mapping before any network request.
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    try:
        lookup.receipt_identity(path,binding,selection)
        typ, code = selection['lookup_type'], selection['code']
        if typ != 'enabled_territory' and not typ.startswith(('EXM_','ORA_EXM_')):
            raise ValueError('Selected lookup requires a separately qualified capture route')
        def read(name, endpoint, query):
            request={'method':'GET','path':endpoint,'query':query}
            response=directory/(name+'.json')
            status=get(request,response)
            receipt[name]={'request':request,'http_status':status,'response_file':response.name,
                'response_sha256':digest(response)}
            return lookup.response(path,receipt[name],request)
        if typ == 'enabled_territory':
            data=read('country',lookup.COUNTRY_RESOURCE,{
                'finder':'TerritoryCodeAllRowsFinder;TerritoryCode='+code,'limit':'100'})
            lookup.classify_country(data,code)
        else:
            data=read('parent',lookup.RESOURCE,{'finder':'LookupTypeFinder;LookupType='+typ,'limit':'100'})
            parent=lookup.unique(lookup.complete(data),LookupType=typ)
            if parent.get('ModuleId') != lookup.MODULE:
                raise ValueError('Lookup is outside the Expenses module')
            codes=read('codes',lookup.returned_child(parent,'lookupCodes',binding['origin']),{'limit':'500'})
            selected=lookup.unique(lookup.complete(codes),LookupCode=code)
            context=read('context',lookup.returned_child(selected,'lookupsDFF',binding['origin']),{'limit':'100'})
            lookup.classify_standard(data,codes,context,typ,code)
        path.write_text(json.dumps(receipt,indent=2)+'\n')
        return lookup.verify_selection(path,binding,selection)
    except Exception:
        # Partial responses remain diagnostic evidence, never a successful receipt.
        receipt['status']='failed'
        path.write_text(json.dumps(receipt,indent=2)+'\n')
        raise


def core_get(repo, properties, binding):
    """Use core's bound-token HTTP API with a cache-only, single-request policy.

    The shared CLI owns interactive login/retry behavior; this routed lookup
    intentionally calls its existing request API directly to avoid those flows.
    Tokens stay in memory and never enter command arguments, files or diagnostics.
    """
    repo, properties = Path(repo), Path(properties)
    auth_path=repo/'core/auth/fusion-oauth-authentication/scripts/fusion_auth.py'
    common_path=repo/'core/fusion-api/rest-api-client/scripts/rest_client_common.py'
    sys.path.insert(0,str(auth_path.parent));sys.path.insert(0,str(common_path.parent))
    auth=importlib.import_module('fusion_auth')
    common=importlib.import_module('rest_client_common')
    if Path(auth.__file__).resolve()!=auth_path.resolve() or Path(common.__file__).resolve()!=common_path.resolve():
        raise ValueError('Loaded core transport differs from the selected repository')
    watched=[properties,auth_path,common_path,Path(__file__),Path(lookup.__file__)]
    hashes={p:digest(p) for p in watched}
    props=auth.read_properties(properties)
    if not same_environment(props.get('environment'), binding['environment']) or origin(props.get('restBaseUrl'))!=origin(binding['origin']):
        raise ValueError('Lookup capture profile differs from explicit target')
    def unchanged():
        if any(digest(p)!=sha for p,sha in hashes.items()):
            raise ValueError('Lookup capture profile or transport changed')
    unchanged()
    try:
        # Validate existing trust only: ensure_oauth_trust_policy may enroll and
        # get_access_token may log in. Neither is selected by this lookup step.
        auth.authorized_token_authority(props)
        scoped=common.props_with_scope_property(props,'scope')
        token=auth.load_cached_access_token(scoped,auth.token_cache_path(scoped,'auto'))
    except Exception:
        raise LookupTransportError('auth_authz','Existing authorized token cache is unavailable; use the routed authentication workflow separately') from None
    if not token:
        raise LookupTransportError('auth_authz','No current cached token; use the routed authentication workflow separately')
    bound=auth.BoundAccessToken(token,auth.request_context(scoped))
    def get(request,response):
        unchanged()
        if request.get('method')!='GET' or response.exists() or response.is_symlink():
            raise ValueError('Only fresh read-only lookup capture is permitted')
        path=request.get('path','')
        if path not in {lookup.RESOURCE,lookup.COUNTRY_RESOURCE} and not path.startswith(lookup.RESOURCE+'/'):
            raise ValueError('Request is outside the declared lookup resources')
        url=common.build_url(scoped,origin(binding['origin'])+path,request['query'])
        try:
            content,headers,status=common.request_bytes(scoped,url,method='GET',access_token=bound,
                headers={'REST-Framework-Version':'9'},json_body=None,timeout=20)
        except auth.FusionHttpError as error:
            raise LookupTransportError('auth_authz' if error.status_code in {401,403} else 'fusion_api',
                'Core lookup GET failed with HTTP '+str(error.status_code)+'; no retry or login attempted') from None
        except (OSError,RuntimeError) as error:
            detail=transport_diagnostic(error)
            raise LookupTransportError('transport_environment',
                'Core lookup GET transport failed ('+detail['transport_reason']+'); no retry attempted',
                **detail) from None
        unchanged()
        if status!=200:
            raise LookupTransportError('fusion_api','Core lookup GET did not return HTTP200')
        with response.open('xb') as stream:stream.write(content)
        return status
    return get


def capture_batch(selections, reviews, binding, directory, get, *, unchanged=lambda: None):
    """One invocation, fresh shared GETs, independently verified field receipts.

    Reuse only byte-identical requests within this immutable input/target
    binding. Nothing is reused across runs or after a failed request.
    """
    directory = Path(directory)
    if not selections or len(selections) != len(reviews):
        raise ValueError('Every batch selection requires its consuming review')
    if directory.exists() or directory.is_symlink():
        raise ValueError('Batch capture output must be a new directory')
    directory.mkdir(parents=True)
    responses, index = {}, {}
    network_calls = 0
    def shared_get(request, response):
        nonlocal network_calls
        unchanged()
        key = json.dumps(request, sort_keys=True, separators=(',', ':'))
        if key in responses:
            with Path(response).open('xb') as stream:
                stream.write(responses[key])
            return 200
        network_calls += 1
        status = get(request, response)
        if status == 200:
            responses[key] = Path(response).read_bytes()
        return status
    for number, (selection, review) in enumerate(zip(selections, reviews)):
        output = directory/str(number)
        capture(selection, binding, output, shared_get,
            company_context=review.get('company_context'))
        fields = index.setdefault(selection['entity'], {}).setdefault(
            selection['policy_name'], {}).setdefault(selection['operation'], {})
        fields.setdefault(selection['field'], {})[selection['code']] = str(output/'receipt.json')
    return index, network_calls


def run(args):
    from workbook_intake import ROOT,artifact_output,load_catalog,read_package
    from build_fsm_from_workbook import ensure_task_plan
    from currency_receipt import binding
    import baseline_evidence
    if getattr(args,'dry_run',False) and args.execute:
        raise ValueError('Dry-run cannot execute lookup requests')
    ensure_task_plan()
    selection=json.loads(args.selection.read_text())
    batch = isinstance(selection, list)
    incoming = selection if batch else [selection]
    runtime=json.loads(args.runtime_contract.read_text())
    selections = [encoded_selection(item,runtime) for item in incoming]
    if not batch and selections:
        selection=selections[0]
    if not selections:
        raise ValueError('Lookup batch must contain at least one exact selection')
    if len({json.dumps(s, sort_keys=True) for s in selections}) != len(selections):
        raise ValueError('Duplicate lookup batch selection')
    # Exact task/schema and origin-bound export provenance precede side effects.
    catalog=load_catalog()
    _,grids=read_package(args.baseline_zip,catalog)
    provenance=baseline_evidence.verify(args.baseline_zip,args.baseline_receipt,
        args.baseline_export_plan,args.baseline_export_approval,args.environment,args.baseline_process_id)
    if origin(provenance['origin'])!=origin(args.target_origin):
        raise ValueError('Lookup target differs from the verified baseline origin')
    rows={entity:[dict(zip(catalog['entities'][entity],row)) for row in grid[1:]]
        for entity,grid in grids.items()}
    selection_reviews=[supplied_selection(args.workbook,s,rows) for s in selections]
    if any(r.get('company_context') is not None for r in selection_reviews):
        from mileage_company_lookup import validate_evidence
        validate_evidence(json.loads(args.runtime_contract.read_text()))
    context={**binding(args.workbook,args.baseline_zip,args.runtime_contract,args.environment,
        args.target_origin,args.validation_date),
        'intake_catalog_sha256':digest(ROOT/'references/intake-fields.json')}
    watched=[args.workbook,args.baseline_zip,args.runtime_contract,args.selection,
        args.baseline_receipt,args.baseline_export_plan,args.baseline_export_approval,
        args.properties,ROOT/'references/intake-fields.json']
    hashes={p:digest(p) for p in watched}
    def unchanged():
        if any(digest(p)!=value for p,value in hashes.items()):
            raise ValueError('Lookup preparation inputs changed; prepare a new plan')
    directory=artifact_output(args.output_dir,args.project_root)
    if getattr(args,'dry_run',False):
        print(json.dumps({'status':'validated_lookup_plan','selections':len(selections),
            'network_calls':0,'writes':0,'import_approved':False}))
        return 0
    directory.mkdir(parents=True,exist_ok=False)
    plan={'schema_version':'1.0','route':lookup.ROUTE,'binding':context,
        **({'selections':selections,'selection_reviews':selection_reviews} if batch else
           {'selection':selection,'selection_review':selection_reviews[0]}),
        'input_sha256':{str(p):value for p,value in hashes.items()},
        'selection_encodings':[{'input':before,'encoded':after}
            for before,after in zip(incoming,selections) if before!=after],
        'side_effect':'Read-only reference GETs and local evidence; no policy mutation or import',
        'capture_boundary':'Supplied fields or exact retained parent fields selected by workbook policy/rate rows. Mileage company bundles derive the exact parent list and all existing consumed child codes; no newly invented reference values.'}
    (directory/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    if not args.execute:
        print(json.dumps({'status':'planned','network_calls':0,'import_approved':False}))
        return 0
    try:
        unchanged()
        repo=next(p for p in ROOT.parents if (p/'core/auth/fusion-oauth-authentication/scripts/fusion_auth.py').is_file())
        get=core_get(repo,args.properties,context)
        def checked_get(request,response):
            unchanged(); status=get(request,response); unchanged(); return status
        if batch:
            index, network_calls = capture_batch(selections,selection_reviews,context,
                directory/'captures',checked_get,unchanged=unchanged)
        else:
            capture(selection,context,directory/'capture',checked_get,
                company_context=selection_reviews[0].get('company_context'))
            index={selection['entity']:{selection['policy_name']:{selection['operation']:{
                selection['field']:str(directory/'capture/receipt.json')}}}}
        unchanged()
        (directory/'lookup-receipts.json').write_text(json.dumps(index,indent=2)+'\n')
        print(json.dumps({'status':'captured','reference_resolved':True,'import_approved':False,
            **({'selections':len(selections),'network_calls':network_calls} if batch else {})}))
        return 0
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:
        (directory/'failure.json').write_text(json.dumps({'status':'blocked','stage':'reference_lookup',
            'failure_class':getattr(error,'failure_class','transport_environment' if isinstance(error,subprocess.TimeoutExpired) else 'input_validation'),
            'message':str(error),'recommended_action':'Inspect the recorded failure; no automatic retry or substitute eligibility.',
            **getattr(error,'diagnostic',{})},indent=2)+'\n')
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('workbook','baseline-zip','runtime-contract','selection','properties','output-dir',
                 'project-root','baseline-receipt','baseline-export-plan','baseline-export-approval'):
        parser.add_argument('--'+name,type=Path,required=True)
    for name in ('environment','target-origin','validation-date','baseline-process-id'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--execute',action='store_true',help='Execute only at the routed reference-lookup step; default writes a plan')
    parser.add_argument('--dry-run',action='store_true',help='Validate all selections and the destination without writes or network calls; cannot combine with --execute')
    return run(parser.parse_args())


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:
        print(json.dumps({'status':'blocked','stage':'reference_lookup',
            'failure_class':getattr(error,'failure_class','transport_environment' if isinstance(error,subprocess.TimeoutExpired) else 'input_validation'),
            'message':str(error),'import_approved':False,**getattr(error,'diagnostic',{})}))
        raise SystemExit(2)
