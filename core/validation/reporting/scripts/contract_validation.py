"""Fail-closed validator for the JSON Schema subset used by FSCR validation contracts.

Not a general JSON Schema implementation. Unknown assertion keywords/formats
are rejected so extending a contract cannot silently weaken validation.
"""
from datetime import datetime
import re
from urllib.parse import urlparse


class ContractError(ValueError):
    pass


ANNOTATIONS = {'$schema','$id','$comment','title','description','default','examples'}
KEYWORDS = ANNOTATIONS | {'type','properties','required','additionalProperties','items',
    'minItems','maxItems','uniqueItems','minLength','maxLength','pattern','enum','const',
    'minimum','maximum','format','allOf','anyOf','oneOf','not','if','then','else'}


def lint(schema):
    if not isinstance(schema, dict):
        raise ContractError('Unsupported schema shape')
    unknown = set(schema) - KEYWORDS
    if unknown:
        raise ContractError('Unsupported schema keyword: ' + ', '.join(sorted(unknown)))
    if 'format' in schema and schema['format'] not in {'date-time','uri'}:
        raise ContractError('Unsupported schema format')
    for child in schema.get('properties', {}).values():
        lint(child)
    for key in ['items','not','if','then','else']:
        if key in schema:
            lint(schema[key])
    if isinstance(schema.get('additionalProperties'),dict):
        lint(schema['additionalProperties'])
    for key in ['allOf','anyOf','oneOf']:
        for child in schema.get(key,[]):lint(child)


def same(left,right):
    # JSON distinguishes booleans from numbers; Python equality does not.
    if isinstance(left,bool) != isinstance(right,bool): return False
    return left == right


def matches_type(value, kind):
    return {'object':lambda:isinstance(value,dict), 'array':lambda:isinstance(value,list),
            'string':lambda:isinstance(value,str), 'boolean':lambda:isinstance(value,bool),
            'null':lambda:value is None, 'integer':lambda:isinstance(value,int) and not isinstance(value,bool),
            'number':lambda:isinstance(value,(int,float)) and not isinstance(value,bool)}[kind]()


def validate(value, schema, path='root', *, preflight=True):
    if preflight:lint(schema)
    def fail(keyword):raise ContractError(f'invalid field {path} ({keyword})')
    def valid(part):
        try:validate(value,part,path,preflight=False);return True
        except ContractError:return False
    if 'type' in schema:
        kinds=schema['type'] if isinstance(schema['type'],list) else [schema['type']]
        if not any(matches_type(value,k) for k in kinds):fail('type')
    if 'enum' in schema and not any(same(value,option) for option in schema['enum']):fail('enum')
    if 'const' in schema and not same(value,schema['const']):fail('const')
    if 'allOf' in schema and not all(valid(p) for p in schema['allOf']):fail('allOf')
    if 'anyOf' in schema and not any(valid(p) for p in schema['anyOf']):fail('anyOf')
    if 'oneOf' in schema and sum(valid(p) for p in schema['oneOf']) != 1:fail('oneOf')
    if 'not' in schema and valid(schema['not']):fail('not')
    if 'if' in schema:
        branch='then' if valid(schema['if']) else 'else'
        if branch in schema and not valid(schema[branch]):fail(branch)
    if isinstance(value,dict):
        if any(key not in value for key in schema.get('required',[])):fail('required')
        properties=schema.get('properties',{})
        for key,item in value.items():
            if key in properties:
                validate(item,properties[key],path+'/'+key,preflight=False)
            elif schema.get('additionalProperties') is False:fail('additionalProperties')
            elif isinstance(schema.get('additionalProperties'),dict):
                validate(item,schema['additionalProperties'],path+'/'+key,preflight=False)
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0) or len(value)>schema.get('maxItems',float('inf')):fail('items count')
        if schema.get('uniqueItems') and any(any(same(x,y) for y in value[:i]) for i,x in enumerate(value)):fail('uniqueItems')
        if 'items' in schema:
            for index,item in enumerate(value):validate(item,schema['items'],path+'/'+str(index),preflight=False)
    if isinstance(value,str):
        if len(value)<schema.get('minLength',0) or len(value)>schema.get('maxLength',float('inf')):fail('length')
        if 'pattern' in schema and not re.search(schema['pattern'],value):fail('pattern')
        if schema.get('format')=='date-time':
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})',value):fail('date-time')
            try:
                if datetime.fromisoformat(value.upper().replace('Z','+00:00')).tzinfo is None:fail('date-time')
            except ValueError:fail('date-time')
        if schema.get('format')=='uri' and not urlparse(value).scheme:fail('uri')
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if value<schema.get('minimum',-float('inf')) or value>schema.get('maximum',float('inf')):fail('range')
