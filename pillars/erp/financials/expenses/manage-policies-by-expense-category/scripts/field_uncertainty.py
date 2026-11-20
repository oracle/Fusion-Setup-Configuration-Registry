"""Exact-field application-validation decisions; never import approval.

The host records a decision only after the implementor explicitly accepts the
displayed plan. Every request remains evidence_unresolved after acceptance.
"""
import hashlib
import json
from pathlib import Path

AUDIT = {'CreatedBy','CreationDate','LastUpdatedBy','LastUpdateDate','LastUpdateLogin'}
PROTECTED = AUDIT | {'Status','StartDate','EndDate','CurrencyCode','CurrencyOptionCode'}


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')


class FieldAcceptanceRequired(ValueError):
    failure_class='evidence_unresolved'
    def __init__(self,plan):
        self.plan=plan
        super().__init__('Exact implementor acceptance required for evidence-unresolved fields: '+
            ', '.join(r['entity']+'.'+r['field'] for r in plan['requests'])+
            '; review plan '+plan['plan_sha256']+' before native preview')


def request(entity,operation,field,before,after,current,contract):
    """Return an eligible request only after hard operation/field controls."""
    rule=current.get('fields',{}).get(field,{})
    declaration=rule.get('application_validation',{})
    if (operation!='update' or rule.get('update')!='unresolved'
            or field in set(current.get('identity_fields',[])) | PROTECTED
            or field.endswith('.PolicyName') or field.endswith('Id')
            or declaration.get('kind')!='field_operation'
            or declaration.get('override_eligible') is not True
            or rule.get('role')!='business'
            or current.get('ready') is not True or operation not in current.get('operations',[])):
        raise ValueError(entity+'.'+field+': field is not eligible for application-validation acceptance')
    for key in ('uncertainty','failure_surface'):
        if not isinstance(declaration.get(key),str) or not declaration[key].strip():
            raise ValueError('Application-validation field needs an exact '+key)
    ids=declaration.get('source_ids')
    if not isinstance(ids,list) or not ids or any(not contract.get('sources',{}).get(i) for i in ids):
        raise ValueError('Application-validation field requires registered ownership/context evidence')
    identity=current['identity_fields']
    if any(before.get(f)!=after.get(f) for f in identity):
        raise ValueError('Application-validation acceptance cannot change identity')
    return {'entity':entity,'operation':operation,'target_key':{f:before[f] for f in identity},
        'field':field,'before':before[field],'after':after[field],
        'uncertainty':declaration['uncertainty'],'failure_surface':declaration['failure_surface'],
        'source_ids':ids,'disposition':'evidence_unresolved'}


def plan(requests,binding,candidate_sha256):
    payload={'schema_version':'1.0','task_code':'ORA_EXM_MANAGE_POLICIES_BY_EXPENSE_CATEGORY',
        'binding':binding,'candidate_sha256':candidate_sha256,'requests':requests,
        'boundary':'Field uncertainty acceptance only; native immutable preview, exact candidate approval, one submission, diagnostics and fresh-export reconciliation remain required. No automatic retry.'}
    return {**payload,'plan_sha256':hashlib.sha256(canonical(payload)).hexdigest()}


def load(path):
    p=Path(path)
    if not p.is_absolute() or p.is_symlink() or not p.is_file():
        raise ValueError('Field acceptance requires an absolute regular local file')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate field acceptance JSON key')
            result[key]=value
        return result
    return json.loads(p.read_text(),object_pairs_hook=unique)


def verify(document,expected):
    if not expected['requests']:
        if document is not None:raise ValueError('Unused field acceptance cannot be carried into another candidate')
        return None
    if document is None:raise FieldAcceptanceRequired(expected)
    if (not isinstance(document,dict) or set(document)!={'schema_version','plan','implementor_approval','acknowledgement'}
            or document['schema_version']!='1.0' or document['plan']!=expected
            or document['implementor_approval']!='accept-evidence-uncertainty'
            or not isinstance(document['acknowledgement'],str) or not document['acknowledgement'].strip()):
        raise ValueError('Field acceptance must match the exact displayed plan and explicit implementor decision')
    return {'plan':expected,'acknowledgement':document['acknowledgement'],
        'implementor_approval':'accept-evidence-uncertainty','import_approved':False}
