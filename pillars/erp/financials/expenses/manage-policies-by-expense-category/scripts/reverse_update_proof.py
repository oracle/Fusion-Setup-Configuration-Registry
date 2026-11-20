"""Verify an explicit reverse workbook restores only a forward update's fields.

This is local proof, never rollback, reference evidence or execution authority.
The normal workbook builder independently validates the fresh reverse request.
"""
from collections import Counter
import hashlib
import json
import re
from pathlib import Path
from environment_identity import same_environment

SCHEMA='fscr-policy-reverse-update-proof-v1'
NAMES={'before','forward_blueprint','forward_candidate'}
ENTITIES={'ORA_EXM_CARRENTAL_POLICY','ORA_EXM_CARRENTAL_POLICY_LINE',
          'ORA_EXM_AIRFARE_POLICY','ORA_EXM_AIRFARE_POLICY_LINE',
          'ORA_EXM_MISCELLANEOUS_POLICY','ORA_EXM_MISCELLANEOUS_POLICY_LINE',
          'ORA_EXM_MILEAGE_POLICY','ORA_EXM_MILEAGE_LINE',
          'ORA_EXM_PERDIEM_POLICY','ORA_EXM_PERDIEM_POLICY_LINE',
          'ORA_EXM_PER_DIEM_POLICY_VALUE'}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def load(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate reverse proof key')
            result[key]=value
        return result
    p=Path(path)
    if not p.is_absolute() or p.is_symlink() or not p.is_file():raise ValueError('Unsafe reverse proof path')
    value=json.loads(p.read_text(),object_pairs_hook=unique)
    if not isinstance(value,dict) or set(value)!={'schemaVersion','artifacts'} or value['schemaVersion']!=SCHEMA:
        raise ValueError('Invalid reverse proof envelope')
    artifacts=value['artifacts']
    if not isinstance(artifacts,dict) or set(artifacts)!=NAMES:raise ValueError('Exact forward artifacts required')
    for name,ref in artifacts.items():
        if (not isinstance(ref,dict) or set(ref)!={'path','sha256'} or not isinstance(ref['path'],str)
                or not isinstance(ref['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',ref['sha256'])):
            raise ValueError('Invalid reverse artifact reference')
        source=Path(ref['path'])
        if not source.is_absolute() or source.is_symlink() or not source.is_file() or digest(source)!=ref['sha256']:
            raise ValueError('Reverse proof artifact changed: '+name)
    return artifacts

def verify(path,current,reverse_operations,protocol,runtime,read_rows,canonical,context):
    from workbook_intake import checked_zip,xml
    proof_sha=digest(path);current_sha=digest(current)
    artifacts=load(path)
    forward=json.loads(Path(artifacts['forward_blueprint']['path']).read_text())
    if not isinstance(forward,dict) or forward.get('task')!={k:protocol['task'][k] for k in ('name','code')}:
        raise ValueError('Reverse proof task mismatch')
    scope=forward.get('resolvedScope',{})
    bound=scope.get('policyPreparation',{})
    if (not same_environment(bound.get('environment'), context.get('environment')) or bound.get('target_origin') != context.get('target_origin')) or not context.get('environment') or not context.get('target_origin'):
        raise ValueError('Reverse proof target lineage mismatch')
    if scope.get('inputBindings',{}).get('baseline')!=artifacts['before']['sha256']:
        raise ValueError('Forward blueprint baseline binding mismatch')
    metadata=[]
    for source in (artifacts['before']['path'],artifacts['forward_candidate']['path'],current):
        with checked_zip(source) as archive:raw=archive.read(protocol['package']['metadataMember'])
        root=xml(raw)
        for tag,expected in [('ProcessEnv',context['environment']),('ObjectShortName',protocol['task']['code'])]:
            values=[node.text for node in root.iter() if node.tag.rsplit('}',1)[-1]==tag]
            if (len(values) != 1 or (not same_environment(values[0], expected) if tag == 'ProcessEnv' else values[0] != expected)):
                raise ValueError('Reverse proof package target/task identity mismatch')
        metadata.append(raw)
    if metadata[0]!=metadata[1]:raise ValueError('Forward candidate changed submission metadata')
    initial,candidate,persisted=[read_rows(p) for p in
        (artifacts['before']['path'],artifacts['forward_candidate']['path'],current)]
    entities={e['name']:e for e in protocol['package']['entities']}
    def key(name,row):
        return tuple(canonical(entities[name],f,row.get(f,''),protocol)
                     for f in runtime['entities'][name]['identity_fields'])
    def index(operations):
        found={}
        if not isinstance(operations,list) or not operations:raise ValueError('Nonempty reverse updates required')
        for op in operations:
            name=op.get('entity')
            if name not in ENTITIES or op.get('action')!='update' or not isinstance(op.get('targetKey'),dict) or not isinstance(op.get('values'),dict) or not op['values']:
                raise ValueError('Only explicit reviewed policy business updates can be reversed')
            if name not in runtime.get('entities',{}):
                raise ValueError('Reverse update requires a reviewed runtime identity contract')
            identity=runtime['entities'][name]['identity_fields']
            if set(op['targetKey'])!=set(identity) or set(op['values']) & (set(identity)|set(entities[name]['auditFields'])):
                raise ValueError('Reverse update key/audit boundary')
            k=(name,key(name,op['targetKey']))
            if k in found:raise ValueError('Duplicate reverse update target')
            found[k]=op
        return found
    left,right=index(forward.get('operations')),index(reverse_operations)
    if set(left)!=set(right):raise ValueError('Reverse update targets differ from forward update')
    for (name,identity),op in left.items():
        reverse=right[name,identity]
        if set(op['values'])!=set(reverse['values']):raise ValueError('Reverse update fields differ from forward update')
        selected=[]
        for source in (initial,candidate,persisted):
            matches=[row for row in source[name] if key(name,row)==identity]
            if len(matches)!=1:raise ValueError('Forward proof target absent or ambiguous')
            selected.append(matches[0])
        before,submitted,after=selected
        for field in entities[name]['headers']:
            if field in entities[name]['auditFields']:continue
            expected=op['values'].get(field,before[field])
            if any(canonical(entities[name],field,row[field],protocol)!=canonical(entities[name],field,expected,protocol) for row in (submitted,after)):
                raise ValueError('Forward value or preservation is not verified')
        for field,value in reverse['values'].items():
            if canonical(entities[name],field,value,protocol)!=canonical(entities[name],field,before[field],protocol):
                raise ValueError('Reverse value does not restore the original baseline')
    for name,entity in entities.items():
        fields=[f for f in entity['headers'] if f not in entity['auditFields']]
        def protected(row):return name not in ENTITIES or name not in runtime.get('entities',{}) or (name,key(name,row)) not in left
        def counts(source):return Counter(tuple(canonical(entity,f,row[f],protocol) for f in fields)
            for row in source[name] if protected(row))
        if counts(initial)-counts(persisted):raise ValueError('Forward proof removed or altered a protected row')
    if load(path)!=artifacts or digest(path)!=proof_sha or digest(current)!=current_sha:
        raise ValueError('Reverse proof inputs changed during verification')
    return {'schemaVersion':'fscr-public-reverse-update-proof-v1','restorationVerified':True,
        'forwardDesignSha256':canonical_digest(forward),'forwardBlueprintSha256':artifacts['forward_blueprint']['sha256'],
        'beforeSha256':artifacts['before']['sha256'],'forwardCandidateSha256':artifacts['forward_candidate']['sha256'],
        'currentSha256':current_sha,'reverseOperationsSha256':canonical_digest(reverse_operations),
        'proofSha256':proof_sha,'authority':'Local restoration proof only; fresh reverse references, exact field acceptance, native validation and separate import approval remain mandatory.'}
