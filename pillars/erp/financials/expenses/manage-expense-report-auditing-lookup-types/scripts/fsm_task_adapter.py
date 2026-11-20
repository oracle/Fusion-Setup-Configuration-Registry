"""Offline protocol bridge to the customer workbook runtime. Never submits to Fusion."""
from __future__ import annotations
import sys as _artifact_sys
from pathlib import Path as _ArtifactPath
_artifact_sys.path.insert(0, str(_ArtifactPath(__file__).resolve().parent))
from artifact_publication import publish_files as _publish_artifact_files, publish_json as _publish_artifact_json
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

# Resolve sibling helpers without depending on the caller's current directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import workbook_schema_adapter as schema
import intake_workbook as intake
import build_import_candidate as customer

AdapterError = schema.AdapterError
SCHEMA_VERSION = schema.SCHEMA_VERSION
ENTITY = 'FUN_APP_GENERIC_LOOKUP'
KEY = ('LookupType', 'LookupCode', 'ViewApplicationId', 'SetCode')
AUDIT = {'CreatedBy', 'CreationDate', 'LastUpdateDate', 'LastUpdateLogin', 'LastUpdatedBy'}
CLEAR = AUDIT | {'UpdateStartDate'}
FIELDS = {'Meaning':'meaning', 'Description':'description', 'EnabledFlag':'enabled',
          'StartDateActive':'start_date', 'EndDateActive':'end_date',
          'DisplaySequence':'display_sequence', 'Tag':'tag'}
DERIVED = {'ModuleKey':'EXM', 'ModuleType':'APPLICATION', 'ChangeSinceLastRefresh':'N'}


def __getattr__(name):
    # Source-field helpers remain available to the tester's scalar fixture checks.
    # Public build/validate/reconcile functions below never delegate generic writes.
    return getattr(schema, name)


def _load_contract(path):
    contract = schema._read_json(Path(path))
    if contract.get("schemaVersion") not in (SCHEMA_VERSION, "fscr-fsm-task-adapter-v2"):
        raise AdapterError('Unsupported adapter schema: '+str(contract.get('schemaVersion')))
    return schema._load_contract(Path(path))


def _snapshot(path, environment):
    if path is None:
        raise AdapterError('A fresh --reference-snapshot is required; an FSM export cannot establish destination permissions or complete reference data.')
    value = schema._read_json(Path(path))
    if not isinstance(value, dict) or value.get('environment') != environment:
        raise AdapterError('Reference snapshot environment does not match the selected export.')
    return value


def _model(blueprint):
    rows=[]
    for op in blueprint['operations']:
        if op['entity'] != ENTITY:
            raise AdapterError('This adapter qualifies code create/update only. Parent-text and independent translation tests require a separate evidence-backed adapter scope; the customer workbook functionality is unchanged.')
        row={'lookup_type':op['targetKey']['LookupType'], 'lookup_code':op['targetKey']['LookupCode'], 'set_code':op['targetKey']['SetCode']}
        for field, value in op['values'].items():
            if field in KEY:
                if str(value) != str(op['targetKey'][field]):
                    raise AdapterError('A supplied key value conflicts with targetKey.')
            elif field in DERIVED:
                if op['action'] != 'create' or str(value) != DERIVED[field]:
                    raise AdapterError('Derived module/refresh fields are not editable workbook inputs.')
            elif field in FIELDS:
                if value in ('', None):
                    raise AdapterError('Explicit clearing is not supported by the workbook; omit unchanged values.')
                row[FIELDS[field]] = ('Yes' if value == 'Y' else 'No') if field == 'EnabledFlag' else value
            else:
                raise AdapterError('Field is not exposed by the workbook: '+field)
        rows.append(row)
    return {'task_code':intake.TASK, 'rows':rows, 'source_issues':[]}


def _context(contract, baseline_path, blueprint, snapshot_path):
    baseline=schema._read_package(Path(baseline_path), contract)
    schema._validate_blueprint(contract, blueprint, baseline)
    environment=baseline.metadata['ProcessEnv']
    snap=_snapshot(snapshot_path, environment)
    if snap.get('baseline_sha256') != schema._sha256_path(Path(baseline_path)):
        raise AdapterError('Reference snapshot is not bound to this baseline.')
    model=_model(blueprint)
    checks=intake.preflight(model, snap, environment)
    if checks['status'] != 'ready_for_design_review':
        raise AdapterError('Workbook preflight blocked: '+json.dumps(checks['issues']))
    for op,resolved in zip(blueprint['operations'],checks['resolved_rows']):
        if op['action'] != resolved['operation'] or any(str(op['targetKey'][k])!=str(resolved['identity'][k]) for k in KEY):
            raise AdapterError('Requested operation/identity conflicts with destination preflight.')
    entity=schema._entity_map(contract)[ENTITY]
    prior=schema._row_index(baseline,entity)
    for op in blueprint['operations']:
        old=prior.get(tuple(str(op['targetKey'][k]) for k in entity['keyFields']))
        if old is None:continue
        set_id=next(v['SetId'] for v in snap['sets'] if v['SetCode']==op['targetKey']['SetCode'])
        fresh=next(v for v in snap['codes'] if v['LookupType']==op['targetKey']['LookupType'] and v['LookupCode']==op['targetKey']['LookupCode'] and str(v['ViewApplicationId'])==str(op['targetKey']['ViewApplicationId']) and str(v['SetId'])==str(set_id))
        for field in FIELDS:
            if field in fresh and _canonical(field,old[field])!=_canonical(field,fresh[field]):
                raise AdapterError('Baseline and fresh destination evidence disagree: '+field)
    return baseline, model, snap, checks


def normalize_design(contract, baseline_path, request_path, design_path, reference_snapshot=None):
    blueprint,preview,requirements=schema.normalize_design(contract, Path(baseline_path), Path(request_path), Path(design_path))
    _context(contract,baseline_path,blueprint,reference_snapshot)
    preview['referenceSnapshotSha256']=schema._sha256_path(Path(reference_snapshot))
    preview['prerequisiteEvidence']='Destination snapshot checked by the customer workbook preflight; supply fresh evidence again when building.'
    return blueprint,preview,requirements


def _canonical(field,value):
    text='' if value is None else str(value)
    if field in ('StartDateActive','EndDateActive') and text:
        return customer.import_date(text)
    return text


def _expected(contract,baseline,blueprint):
    """Independent row oracle; does not call the customer builder or its row plan."""
    entities=schema._entity_map(contract)
    original={name:schema._row_index(baseline,entity) for name,entity in entities.items()}
    output={name:{} for name in entities}
    code=entities[ENTITY]
    for op in blueprint['operations']:
        ident=tuple(str(op['targetKey'][k]) for k in KEY)
        indexed_ident=tuple(str(op['targetKey'][k]) for k in code['keyFields'])
        before=original[ENTITY].get(indexed_ident)
        # Blank worksheet fields preserve; no-op operations produce no package row.
        if before is not None and all(_canonical(k,before.get(k))==_canonical(k,v) for k,v in op['values'].items()):
            continue
        row=dict(before) if before is not None else {h:'' for h in code['headers']}
        row.update({k:str(v) for k,v in op['targetKey'].items()})
        row.update({k:str(v) for k,v in op['values'].items()})
        row.update(ModuleKey='EXM',ModuleType='APPLICATION')
        if before is None:
            row.setdefault('EnabledFlag','Y')
            if not row['EnabledFlag']:row['EnabledFlag']='Y'
            row['ChangeSinceLastRefresh']='N'
        for k in CLEAR:row[k]=''
        for k in ('StartDateActive','EndDateActive'):row[k]=_canonical(k,row[k])
        output[ENTITY][indexed_ident]=row
        tlname='FUN_APP_GENERIC_LOOKUP_TRANSLATION'
        for tlkey,tl in original[tlname].items():
            if tuple(tl['FUN_APP_GENERIC_LOOKUP.'+k] for k in KEY)==ident:
                if {'Meaning','Description'} & set(op['values']):
                    raise AdapterError('Translation text edits are outside the workbook contract.')
                output[tlname][tlkey]=dict(tl)
    return output


def _validation(contract,template_path,baseline_path,blueprint_path,requirements_path,candidate_path,reference_snapshot):
    blueprint=schema._read_json(Path(blueprint_path));requirements=schema._read_json(Path(requirements_path))
    baseline,model,snap,checks=_context(contract,baseline_path,blueprint,reference_snapshot)
    schema._requirement_contract(contract,blueprint,requirements)
    template=schema._read_package(Path(template_path),contract)
    candidate=schema._read_package(Path(candidate_path),contract)
    schema._validate_source_pair(contract,template,baseline)
    if snap.get('template_sha256')!=schema._sha256_path(Path(template_path)):
        raise AdapterError('Reference snapshot is not bound to this template.')
    expected=_expected(contract,baseline,blueprint)
    errors=[]
    for name,entity in schema._entity_map(contract).items():
        actual=schema._row_index(candidate,entity)
        if actual!=expected[name]:errors.append({'code':'WORKBOOK_ROW_MISMATCH','message':name+' candidate rows differ from requested values and preserved baseline.'})
    metadata=contract['package']['metadataMember']
    if candidate.member_bytes[metadata]!=template.member_bytes[metadata]:
        errors.append({'code':'METADATA_PROVENANCE','message':'Workbook candidate metadata must match the approved template.'})
    return {'schemaVersion':SCHEMA_VERSION,'status':'FAIL' if errors else 'PASS','task':contract['task'],
            'candidateSha256':candidate.archive_sha256,'templateSha256':template.archive_sha256,
            'baselineSha256':baseline.archive_sha256,'designSha256':schema._sha256_bytes(schema._canonical_bytes(blueprint)),
            'referenceSnapshotSha256':schema._sha256_path(Path(reference_snapshot)),
            'schemaFingerprint':schema._schema_fingerprint(contract,template),'memberInventory':candidate.member_names,
            'rowCounts':{e['member']:len(candidate.rows[e['name']]) for e in contract['package']['entities']},
            'requirementIds':[r['id'] for r in requirements],'errors':errors,'warnings':blueprint.get('warnings',[]),
            'unresolvedWarnings':blueprint.get('warnings',[])}


def validate_candidate(contract,template_path,baseline_path,blueprint_path,requirements_path,candidate_path,reference_snapshot=None):
    return _validation(contract,template_path,baseline_path,blueprint_path,requirements_path,candidate_path,reference_snapshot)


def build_candidate(contract,template_path,baseline_path,blueprint_path,requirements_path,output_path,reference_snapshot=None):
    output_path=Path(output_path)
    schema._validate_new_outputs([output_path],[Path(p) for p in (template_path,baseline_path,blueprint_path,requirements_path)]+([Path(reference_snapshot)] if reference_snapshot else []))
    blueprint=schema._read_json(Path(blueprint_path));requirements=schema._read_json(Path(requirements_path))
    baseline,model,snap,checks=_context(contract,baseline_path,blueprint,reference_snapshot)
    schema._requirement_contract(contract,blueprint,requirements)
    if not any(r['changes'] for r in checks['resolved_rows']):
        return {'schemaVersion':SCHEMA_VERSION,'status':'NO_OP','task':contract['task'],'reason':'No changed workbook rows; no candidate written.'}
    model=dict(model,rows=sorted(model['rows'],key=lambda row:(row['lookup_type'],row['set_code'],row['lookup_code'])))
    try:data,_=customer.build(model,snap,Path(template_path),Path(baseline_path),baseline.metadata['ProcessEnv'])
    except (ValueError,KeyError,StopIteration) as exc:raise AdapterError(str(exc)) from exc
    with tempfile.TemporaryDirectory(prefix='lookup-adapter-') as directory:
        temporary=Path(directory)/'candidate.zip';temporary.write_bytes(data)
        result=validate_candidate(contract,template_path,baseline_path,blueprint_path,requirements_path,temporary,reference_snapshot)
        if result['status']!='PASS':raise AdapterError('Customer candidate failed independent validation: '+json.dumps(result['errors']))
    _publish_artifact_files({output_path: data})
    result.update(businessSummary=blueprint['operations'],structuralValidator='generated exact-task package reader',semanticValidator='independent workbook operation/baseline row oracle',notImported=True)
    return result


def determinism_check(contract,template_path,baseline_path,blueprint_path,requirements_path,reference_snapshot=None):
    with tempfile.TemporaryDirectory(prefix='lookup-determinism-') as directory:
        paths=[Path(directory)/name for name in ('a.zip','b.zip')]
        results=[build_candidate(contract,template_path,baseline_path,blueprint_path,requirements_path,p,reference_snapshot) for p in paths]
        if all(r['status']=='NO_OP' for r in results):return {'status':'PASS','identicalBytes':True,'noOp':True}
        hashes=[schema._sha256_path(p) for p in paths]
    return {'status':'PASS' if hashes[0]==hashes[1] else 'FAIL','identicalBytes':hashes[0]==hashes[1],'firstSha256':hashes[0],'secondSha256':hashes[1]}


def reconcile(contract,baseline_path,candidate_path,blueprint_path,requirements_path,export_path):
    # Reconciliation uses persisted evidence only; expired pre-import snapshots
    # cannot prevent checking an already-submitted outcome.
    baseline=schema._read_package(Path(baseline_path),contract);candidate=schema._read_package(Path(candidate_path),contract);persisted=schema._read_package(Path(export_path),contract)
    if persisted.metadata['ProcessEnv']!=baseline.metadata['ProcessEnv'] or persisted.metadata['ProcessRelease']!=baseline.metadata['ProcessRelease']:
        raise AdapterError('Readback environment/release does not match the baseline.')
    blueprint=schema._read_json(Path(blueprint_path));requirements=schema._read_json(Path(requirements_path))
    schema._validate_blueprint(contract,blueprint,baseline);schema._requirement_contract(contract,blueprint,requirements)
    expected=_expected(contract,baseline,blueprint);entities=schema._entity_map(contract)
    indexes={n:{'before':schema._row_index(baseline,e),'candidate':schema._row_index(candidate,e),'persisted':schema._row_index(persisted,e)} for n,e in entities.items()}
    operations={op['id']:op for op in blueprint['operations']};matrix=[]
    creates={(op['entity'],tuple(str(op['targetKey'][k]) for k in entities[op['entity']]['keyFields']))
             for op in blueprint['operations'] if op['action']=='create'}
    touched={(op['entity'],tuple(str(op['targetKey'][k]) for k in entities[op['entity']]['keyFields'])) for op in blueprint['operations']}
    for req in requirements:
        name=req['entity'];entity=entities[name];key=tuple(str(req['targetKey'][k]) for k in entity['keyFields']);ix=indexes[name]
        before=ix['before'].get(key);actual=ix['candidate'].get(key) or (before if key not in expected[name] else None);saved=ix['persisted'].get(key);kind=req['kind'];detail=[]
        if kind=='target':passed=actual is not None and saved is not None
        elif kind in ('value','candidate_context'):
            field=req['field'];want=_canonical(field,req['requestedValue']);passed=actual is not None and saved is not None and _canonical(field,actual[field])==want and (kind=='candidate_context' and field in {'ModuleKey','ModuleType'} or _canonical(field,saved[field])==want)
        elif kind=='preserve_target':
            op=operations[req['operationId']];ignored=set(op['values'])|AUDIT|{'UpdateStartDate','ModuleKey','ModuleType'}
            detail=[f for f in entity['headers'] if f not in ignored and (before is None or actual is None or saved is None or _canonical(f,before[f])!=_canonical(f,actual[f]) or _canonical(f,before[f])!=_canonical(f,saved[f]))];passed=not detail
        elif kind=='preserve_rows':
            for en,e in entities.items():
                for ek,old in indexes[en]['before'].items():
                    if (en,ek) in touched:continue
                    new=indexes[en]['persisted'].get(ek)
                    if new is None or any(_canonical(f,old[f])!=_canonical(f,new[f]) for f in e['headers'] if f not in AUDIT):detail.append(en+':'+str(ek))
            passed=not detail
        else:raise AdapterError('Unsupported requirement kind: '+kind)
        matrix.append({'id':req['id'],'requirement':req['requirement'],'requested':req.get('requestedValue','record/preservation'),'candidate':actual,'persisted':saved,'passed':passed,'differences':detail})
    # Candidate tampering and every preserved translation are independently checked.
    errors=[{'code':'CANDIDATE_MISMATCH','message':name} for name in entities if indexes[name]['candidate']!=expected[name]]
    for name,rows in expected.items():
        for key,row in rows.items():
            saved=indexes[name]['persisted'].get(key)
            differences=[f for f in entities[name]['headers'] if f not in AUDIT|{'UpdateStartDate','ModuleKey','ModuleType'} and (saved is None or _canonical(f,row[f])!=_canonical(f,saved[f]))]
            # The import service resolves ModuleKey/ModuleType to ModuleId. Accept
            # that create-only enrichment only when pre-import rows independently
            # establish one exact type/view/module association. Never learn the
            # expected ID from the row being verified or ignore it on updates.
            if (name == ENTITY and (name,key) in creates and not row.get('ModuleId')
                    and saved is not None and 'ModuleId' in differences):
                module_ids={old['ModuleId'] for entity_name in (ENTITY,'ORA_FINANCIALS_GENERIC_LOOKUP_TYPE')
                            for old in baseline.rows.get(entity_name,[])
                            if old.get('LookupType')==row['LookupType']
                            and old.get('ViewApplicationId')==row['ViewApplicationId']
                            and old.get('ModuleKey')==row['ModuleKey']
                            and old.get('ModuleType')==row['ModuleType']
                            and old.get('ModuleId')}
                if len(module_ids)==1 and saved.get('ModuleId') in module_ids:
                    differences.remove('ModuleId')
            if differences:errors.append({'code':'PERSISTED_ROW_MISMATCH','message':name+str(key),'fields':differences})
    mismatches=sum(not r['passed'] for r in matrix)+len(errors)
    return {'schemaVersion':SCHEMA_VERSION,'status':'PASS' if not mismatches else 'FAIL','task':contract['task'],'baselineSha256':baseline.archive_sha256,'candidateSha256':candidate.archive_sha256,'exportSha256':persisted.archive_sha256,'requirementMatrix':matrix,'mismatchCount':mismatches,'errors':errors}


def _exclusive_json(path,value):
    _publish_artifact_json(path, value, newline=False)


def main(argv=None):
    # Keep the standard tester command names; snapshot is an explicit additional
    # task prerequisite, never inferred from CSV or a process-global variable.
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('manifest','normalize','build','validate','determinism','reconcile','rollback'))
    parser.add_argument('--contract',type=Path,default=Path(__file__).resolve().parents[1]/'e2e-adapter.json')
    for name in ('report','package','baseline','template','request','design','blueprint','requirements','output','blueprint-output','preview-output','requirements-output','candidate','export','reference-snapshot'):
        parser.add_argument('--'+name,type=Path)
    parser.add_argument('--environment');parser.add_argument('--base-url');parser.add_argument('--template-only',type=schema._bool_arg)
    args=parser.parse_args(argv)
    try:
        outputs=[args.report]
        if args.command=='build':outputs.append(args.output)
        if args.command=='normalize':outputs.extend([args.blueprint_output,args.preview_output,args.requirements_output])
        inputs=[getattr(args,n) for n in ('contract','package','baseline','template','request','design','blueprint','requirements','candidate','export','reference_snapshot')]
        schema._validate_new_outputs([p for p in outputs if p is not None],[p for p in inputs if p is not None])
        contract=_load_contract(args.contract)
        if args.command=='manifest':result=schema.normalized_manifest(contract,args.package,args.environment,args.base_url,args.template_only)
        elif args.command=='normalize':
            bp,preview,req=normalize_design(contract,args.baseline,args.request,args.design,args.reference_snapshot)
            schema._validate_new_outputs([args.blueprint_output,args.preview_output,args.requirements_output],[args.baseline,args.request,args.design,args.reference_snapshot])
            for path,value in ((args.blueprint_output,bp),(args.preview_output,preview),(args.requirements_output,req)):_exclusive_json(path,value)
            result=preview
        elif args.command=='build':result=build_candidate(contract,args.template,args.baseline,args.blueprint,args.requirements,args.output,args.reference_snapshot)
        elif args.command=='validate':result=validate_candidate(contract,args.template,args.baseline,args.blueprint,args.requirements,args.package,args.reference_snapshot)
        elif args.command=='determinism':result=determinism_check(contract,args.template,args.baseline,args.blueprint,args.requirements,args.reference_snapshot)
        elif args.command=='reconcile':result=reconcile(contract,args.baseline,args.candidate,args.blueprint,args.requirements,args.export)
        else:raise AdapterError('Automatic rollback is not qualified for the workbook bridge. Use fresh reviewed workbook changes through the normal workflow.')
        if args.report:_exclusive_json(args.report,result)
        print(json.dumps(result,indent=2));return 0 if result.get('status','PASS') in ('PASS','COMPLETED','NO_OP') else 2
    except (AdapterError,ValueError,TypeError,KeyError,OSError) as exc:
        print(json.dumps({'status':'FAIL','errors':[{'code':'WORKBOOK_ADAPTER','message':str(exc)}]}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
