"""Offline FSM protocol backed by the ordinary Policies preparation and rules.

No lookup, authentication, submission, approval or Fusion mutation occurs here.
The workbook and its bound evidence remain authoritative at every entrypoint.
"""
from collections import Counter
from pathlib import Path
import copy
import hashlib
import json
import tempfile

from build_fsm_from_workbook import candidate, field_value
from workbook_intake import ROOT, read_workbook, load_catalog, read_package
from metadata_contract import compare, verify_submission_metadata
from environment_identity import same_environment
from accepted_meals_profile import rate_date
from project_artifact_paths import validate_artifact_path

CONTEXT_KEYS = {
    'workbook', 'runtime_contract', 'project_root', 'environment',
    'baseline_process_id', 'baseline_receipt', 'baseline_export_plan',
    'baseline_export_approval', 'currency_receipt', 'target_origin', 'validation_date',
}
FILE_KEYS = CONTEXT_KEYS & {
    'workbook', 'runtime_contract', 'baseline_receipt', 'baseline_export_plan',
    'baseline_export_approval', 'currency_receipt',
}
OPTIONAL_FILE_KEYS = {'lookup_receipts','field_acceptances','reverse_update_of'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def context(scope):
    value = scope.get('policyPreparation') if isinstance(scope, dict) else None
    if (not isinstance(value, dict) or not CONTEXT_KEYS <= set(value)
            or set(value) - CONTEXT_KEYS - OPTIONAL_FILE_KEYS):
        raise ValueError('Exact policyPreparation context and ordinary bound evidence are required')
    for key in CONTEXT_KEYS - {'currency_receipt'}:
        if not isinstance(value[key], str) or not value[key]:
            raise ValueError('Missing policyPreparation input: ' + key)
    for key in FILE_KEYS | (set(value) & OPTIONAL_FILE_KEYS):
        if value[key] is None and key == 'currency_receipt':
            continue
        if not isinstance(value[key], str) or not value[key]:
            raise ValueError('Missing policyPreparation file: ' + key)
        path = Path(value[key])
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise ValueError('Unsafe policyPreparation file: ' + key)
    # Use exactly the ordinary reviewed runtime, never a relaxed caller contract.
    if digest(value['runtime_contract']) != digest(ROOT/'references/fsm-runtime-contract.json'):
        raise ValueError('The task-owned runtime contract is required')
    return dict(value)


def kwargs(ctx):
    result = {
        'expected_environment': ctx['environment'],
        'expected_process_id': ctx['baseline_process_id'],
        **{key: ctx[key] for key in ('baseline_receipt', 'baseline_export_plan',
            'baseline_export_approval', 'currency_receipt', 'target_origin',
            'validation_date', 'project_root')},
    }
    if 'lookup_receipts' in ctx:
        from policy_lookup_preflight import load_receipt_index
        result['lookup_receipts'] = load_receipt_index(ctx['lookup_receipts'])
    if 'field_acceptances' in ctx:result['field_acceptances']=ctx['field_acceptances']
    return result


def prepare(ctx, baseline, output=None):
    return candidate(ctx['workbook'], baseline, ctx['runtime_contract'], output,
                     dry_run=output is None, **kwargs(ctx))


def lookup_bindings(ctx):
    receipt_bindings = {}
    if 'lookup_receipts' in ctx:
        from policy_lookup_preflight import load_receipt_index, receipt_paths
        index = load_receipt_index(ctx['lookup_receipts'])
        receipt_bindings = {'lookupReceiptIndex': digest(ctx['lookup_receipts']),
            'lookupReceipts': {path: digest(path) for path in receipt_paths(index)}}
    if 'field_acceptances' in ctx:receipt_bindings['fieldAcceptances']=digest(ctx['field_acceptances'])
    if 'reverse_update_of' in ctx:
        from reverse_update_proof import load
        receipt_bindings['reverseUpdateProof']={'manifest':digest(ctx['reverse_update_of']),
            'artifacts':load(ctx['reverse_update_of'])}
    return receipt_bindings


def bindings(ctx, baseline):
    owned = [*ROOT.glob('scripts/*.py'), *ROOT.glob('references/*.json'),
             *ROOT.glob('ora-resource/*.md'), *ROOT.glob('ora-resource/*.json')]
    return {'baseline': digest(baseline), **lookup_bindings(ctx), **{
        key: digest(ctx[key]) for key in sorted(FILE_KEYS) if ctx[key] is not None},
        'taskSources': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(owned)},
        'areaSources': {str(p.relative_to(ROOT.parent)): digest(p) for p in
            (ROOT.parent/'scripts/plan_task_rules.py', ROOT.parent/'references/task-rule-execution.md')}}


def product_contract(protocol):
    owned = json.loads((ROOT/'e2e-adapter.json').read_text())
    # The standard noship reader restores test policy only; product fields must
    # remain identical to the actual candidate customer descriptor.
    for key in ('task','package','normalization','semanticModel','reconciliationPolicy',
                'deletionPolicy','entrypoints'):
        if protocol.get(key) != owned.get(key):
            raise ValueError('Adapter product contract differs from the task-owned descriptor: '+key)


def rows(path):
    catalog = load_catalog()
    _, grids = read_package(path, catalog)
    return {e: [dict(zip(grid[0], row)) for row in grid[1:]] for e, grid in grids.items()}


def source_pair(api, protocol, template, baseline):
    """Validate template shape separately from the actual submission descriptor.

    The ordinary builder uses baseline metadata only. Independently exported
    template NodeSequence is retained as provenance and never copied/reordered.
    This does not relax baseline/candidate or persisted metadata comparisons.
    """
    current = api['_read_package'](baseline, protocol)
    manifest(api, protocol, template, current.metadata['ProcessEnv'], '', True)
    rows(template)
    report = compare(template, baseline, {e['name'] for e in protocol['package']['entities']})
    if report['status'] == 'STRUCTURAL_METADATA_DRIFT_STOP':
        raise ValueError('Template and baseline metadata structures differ')
    from workbook_intake import checked_zip, xml
    with checked_zip(template) as archive:
        member=protocol['package']['metadataMember']
        values=[n.text for n in xml(archive.read(member)).iter()
                if n.tag.rsplit('}',1)[-1]=='ObjectShortName']
    if values != [protocol['package']['objectShortName']]:
        raise ValueError('Template belongs to a different setup task')
    return report


def manifest(api, protocol, path, environment, base_url, template_only):
    local = copy.deepcopy(protocol)
    if template_only:
        from workbook_intake import checked_zip, xml
        with checked_zip(path) as archive:
            metadata = xml(archive.read(protocol['package']['metadataMember']))
        actual = api['_metadata_object_contracts'](metadata)
        ownership = json.loads((ROOT/'references/policy-package-metadata.json').read_text())['xmlFileByEntity']
        slots = {}
        for entity in local['package']['entities']:
            source = actual.get(entity['name'])
            if source is None:
                raise ValueError('Template lacks an exact package entity')
            sequence = str(source['nodeSequence'])
            if not sequence.isascii() or not sequence.isdecimal() or int(sequence) < 1:
                raise ValueError('Template sequence must be a positive integer')
            slot = (ownership[entity['name']], source['nodePath'].count('/'), int(sequence))
            if slot in slots and slots[slot] != source['nodePath']:
                raise ValueError('Template has a same-file same-level sequence collision')
            # Two reviewed BO registrations may alias the same exact XML node.
            # Preserve both schemas; neither is independently targeted here.
            slots[slot] = source['nodePath']
            # Intake records an independent template's actual sequence; no
            # template descriptor is ever a submission or reconciliation baseline.
            entity['nodeSequence'] = sequence
        package = api['_read_package'](path, local)
        if any(package.rows.values()):
            raise ValueError('Template-only source contains business rows')
    result = api['_protocol_manifest'](local, path, environment, base_url, template_only)
    package = api['_read_package'](path, local)
    if not same_environment(package.metadata['ProcessEnv'], environment):
        raise ValueError('Manifest environment differs from the actual source export')
    return result


def derive(protocol, ctx, baseline, review):
    """Derive the protocol design from the same validated workbook, not another ruleset."""
    catalog = load_catalog()
    runtime = json.loads(Path(ctx['runtime_contract']).read_text())
    model = read_workbook(ctx['workbook'], catalog)
    current = rows(baseline)
    specs = {(s['entity'], f['csv_field']): f for s in catalog['sheets']
             for f in s['columns'] if f['csv_field']}
    operations = []
    for change in review['changes']:
        entity = change['entity']; rule = runtime['entities'][entity]
        if change.get('generated_new_value_effect'):
            from per_diem_profile import V,REF,VALUE_IDENTITY,validate_evidence
            from per_diem_create import IDS
            validate_evidence(runtime)
            fields={f['field']:f['after']for f in change['fields']}
            if (entity!=V or change.get('source_ids')!=IDS
                    or rule.get('internal_new_policy_value_effects_only')is not True
                    or change['operation']!='create'or set(change['targetKey'])!=set(VALUE_IDENTITY)
                    or set(fields)!={REF,'TypeOfLineCode','DeterminantCode','LineValue'}):
                raise ValueError('Invalid source-owned new Per Diem value effect')
            operations.append({'id':f'OP-{len(operations)+1:03d}','action':'create',
                'entity':V,'targetKey':change['targetKey'],
                'values':{field:value for field,value in fields.items()if field not in VALUE_IDENTITY},
                'preserveOtherValues':True,'preserveUnspecifiedRows':True})
            continue
        if change.get('generated_existing_value_effect'):
            from per_diem_profile import V, SOURCE, VALUE_IDENTITY, validate_evidence
            validate_evidence(runtime)
            if (entity != V or change.get('source_ids') != [SOURCE]
                    or rule.get('internal_existing_value_effects_only') is not True
                    or change['operation'] != 'update' or set(change['targetKey']) != set(VALUE_IDENTITY)
                    or [f['field'] for f in change['fields']] != ['LineValue']):
                raise ValueError('Invalid internal Per Diem existing value effect')
            operations.append({'id': f'OP-{len(operations)+1:03d}', 'action': 'update',
                'entity': V, 'targetKey': change['targetKey'],
                'values': {'LineValue': change['fields'][0]['after']},
                'preserveOtherValues': True, 'preserveUnspecifiedRows': True})
            continue
        matches = [r for r in model['records'] if r['entity'] == entity and r['sources'] == change['sources']]
        if len(matches) != 1:
            raise ValueError('Changed workbook record is ambiguous')
        record = matches[0]
        encoded = {f: field_value(v, rule['fields'][f], specs[entity, f])
                   for f, v in record['values'].items()}
        if entity == 'ORA_EXM_AIRFARE_POLICY_LINE':
            from airfare_profile import existing_identity_context, validate_evidence
            validate_evidence(runtime)
            creating=change['operation']=='create'
            context = existing_identity_context(encoded, current[entity],
                create_allowed=creating and 'create' in rule.get('operations',[]))
            label='create_identity_context' if creating else 'retained_identity_context'
            if (change['operation'] not in rule.get('operations',[])
                    or change.get(label)!=context
                    or creating and context!={'TypeOfRateCode':'CATCH_ALL'}):
                raise ValueError('Airfare identity differs from the validated operation-bound review')
            encoded.update(context)
        if entity == 'ORA_EXM_MISCELLANEOUS_POLICY_LINE':
            from miscellaneous_profile import existing_identity_context, validate_evidence
            validate_evidence(runtime)
            creating=change['operation']=='create'
            context = existing_identity_context(encoded, current[entity],
                create_allowed=creating and 'create'in rule.get('operations',[]))
            label='create_identity_context'if creating else'retained_identity_context'
            if (change['operation']not in rule.get('operations',[])
                    or change.get(label)!=context
                    or creating and any(context.values())):
                raise ValueError('Miscellaneous identity differs from the validated operation-bound review')
            encoded.update(context)
        if entity == 'ORA_EXM_PERDIEM_POLICY_LINE':
            from per_diem_profile import existing_identity_context, validate_evidence
            validate_evidence(runtime)
            creating=change['operation']=='create'
            context = existing_identity_context(encoded,current[entity],create_allowed=creating and'create'in rule.get('operations',[]))
            label='create_identity_context'if creating else'retained_identity_context'
            if change['operation']not in rule.get('operations',[])or change.get(label)!=context:
                raise ValueError('Per Diem identity differs from the validated operation-bound review')
            encoded.update(context)
        identity = rule['identity_fields']
        key = {f: encoded.get(f, '') for f in identity}
        operations.append({'id': f'OP-{len(operations)+1:03d}', 'action': change['operation'],
            'entity': entity, 'targetKey': key,
            'values': {v['field']: v['after'] for v in change['fields'] if v['field'] not in identity},
            'preserveOtherValues': True, 'preserveUnspecifiedRows': True})
    overrides=[]
    field_review=review.get('field_uncertainty_acceptance')
    if field_review:
        for op in operations:
            fields=[r['field'] for r in field_review['plan']['requests']
                if r['entity']==op['entity'] and r['target_key']==op['targetKey']]
            if fields:
                overrides.append({'id':'FIELD-'+op['id'],'operationId':op['id'],'entity':op['entity'],
                    'fields':fields,'implementorApproval':'accept-evidence-uncertainty',
                    'uncertaintyAcknowledgement':field_review['acknowledgement'],
                    'singleSubmissionOnly':True,'automaticRetryAllowed':False})
    reverse={}
    if 'reverse_update_of' in ctx:
        from reverse_update_proof import verify
        proof=verify(ctx['reverse_update_of'],baseline,operations,protocol,
            json.loads(Path(ctx['runtime_contract']).read_text()),rows,canonical,ctx)
        reverse={'reverseUpdateProof':proof,'rollbackOfDesignSha256':proof['forwardDesignSha256']}
    return {**reverse,'task': {k: protocol['task'][k] for k in ('name', 'code')},
        'operations': operations, 'resolvedScope': {'policyPreparation': ctx,
            'inputBindings': bindings(ctx, baseline)},
        'explicitDefaults': [], 'preservedValues': [], 'prerequisites': [],
        'warnings': [{'code': 'POLICY_LIVE_QUALIFICATION_PENDING',
            'message': 'Source-reviewed local validation is not persisted import qualification or approval.'}]+
            [{'code':'EVIDENCE_UNRESOLVED_UPDATE_OVERRIDE','operationId':o['operationId'],
              'entity':o['entity'],'fields':o['fields'],'message':o['uncertaintyAcknowledgement']} for o in overrides],
        'evidenceUnresolvedUpdateOverrides': overrides}


def checked(api, protocol, baseline, blueprint, requirements=None):
    product_contract(protocol)
    if (not isinstance(blueprint, dict) or (requirements is not None and
            (not isinstance(requirements, list) or not all(isinstance(r, dict) for r in requirements)))):
        raise ValueError('Blueprint and requirements must use the declared object/list shapes')
    ctx = context(blueprint.get('resolvedScope'))
    if blueprint['resolvedScope'].get('inputBindings') != bindings(ctx, baseline):
        raise ValueError('Policy preparation inputs changed; normalize and review again')
    review = prepare(ctx, baseline)
    expected = derive(protocol, ctx, baseline, review)
    if blueprint != expected:
        raise ValueError('Blueprint differs from the ordinary validated workbook preparation')
    if requirements is not None and requirements != api['_requirements'](protocol, expected):
        raise ValueError('Requirements differ from the exact validated preparation')
    return ctx, review


def normalize(api, protocol, baseline, request, design):
    product_contract(protocol)
    supplied = api['_read_json'](design)
    ctx = context(supplied.get('resolvedScope'))
    review = prepare(ctx, baseline)
    blueprint = derive(protocol, ctx, baseline, review)
    if 'operations' in supplied and supplied['operations'] != blueprint['operations']:
        raise ValueError('Requested protocol operations differ from the validated workbook')
    requirements = api['_requirements'](protocol, blueprint)
    preview = {'schemaVersion': api['SCHEMA_VERSION'], 'task': blueprint['task'],
        'requestSha256': digest(request), 'designSha256': api['_sha256_bytes'](api['_canonical_bytes'](blueprint)),
        'baselineSha256': digest(baseline), 'operations': blueprint['operations'],
        'explicitDefaults': [], 'prerequisites': [], 'warnings': blueprint['warnings'],
        'requirementCount': len(requirements), 'policyReview': review,
        **({'rollbackOfDesignSha256':blueprint['rollbackOfDesignSha256']} if 'reverseUpdateProof' in blueprint else {}),
        'approvalBoundary': 'Offline preparation only; current Run Book, Task Hook and Data Loader approval remain required.'}
    return blueprint, preview, requirements


def build(api, protocol, template, baseline, blueprint_path, requirements_path, output):
    api['_validate_new_outputs']([output], [template, baseline, blueprint_path, requirements_path])
    source_pair(api, protocol, template, baseline)
    blueprint = api['_read_json'](blueprint_path); requirements = api['_read_json'](requirements_path)
    ctx, review = checked(api, protocol, baseline, blueprint, requirements)
    validate_artifact_path(output, ctx['project_root'])
    # The ordinary builder owns output destination validation and exact sparse CSV shape.
    with tempfile.TemporaryDirectory(prefix='policy-adapter-', dir=Path(ctx['project_root'])/'artifacts') as temp:
        built = prepare(ctx, baseline, Path(temp)/'build')
        data = (Path(temp)/'build/candidate.zip').read_bytes()
        if hashlib.sha256(data).hexdigest() != review['candidate_sha256'] or built['candidate_sha256'] != review['candidate_sha256']:
            raise ValueError('Repeated ordinary preparation changed candidate bytes')
        output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation keeps a conflicting candidate immutable.
        with output.open('xb') as stream:
            stream.write(data)
    return validate(api, protocol, template, baseline, blueprint_path, requirements_path, output)


def validate(api, protocol, template, baseline, blueprint_path, requirements_path, artifact):
    template_review = source_pair(api, protocol, template, baseline)
    api['_read_package'](artifact, protocol)
    blueprint = api['_read_json'](blueprint_path); requirements = api['_read_json'](requirements_path)
    ctx, review = checked(api, protocol, baseline, blueprint, requirements)
    from check_candidate_rules import evaluate
    rules = evaluate(ctx['workbook'], baseline, ctx['runtime_contract'], artifact, **kwargs(ctx))
    verify_submission_metadata(baseline, artifact)
    if digest(artifact) != review['candidate_sha256']:
        raise ValueError('Candidate differs from the exact ordinary policy preparation')
    return {'schemaVersion': api['SCHEMA_VERSION'], 'status': 'PASS', 'task': protocol['task'],
        'candidateSha256': digest(artifact), 'baselineSha256': digest(baseline),
        'designSha256': api['_sha256_bytes'](api['_canonical_bytes'](blueprint)),
        'templateSha256': digest(template), 'requirementIds': [r['id'] for r in requirements],
        'errors': [], 'warnings': blueprint['warnings'], 'policyRuleResults': rules['ruleResults'],
        'notImported': True, 'importApproved': False, 'templateMetadataReview': template_review,
        **({'reverseUpdateProof':blueprint['reverseUpdateProof']} if 'reverseUpdateProof' in blueprint else {})}


def determinism(api, protocol, template, baseline, blueprint_path, requirements_path):
    blueprint = api['_read_json'](blueprint_path); requirements = api['_read_json'](requirements_path)
    ctx, _ = checked(api, protocol, baseline, blueprint, requirements)
    with tempfile.TemporaryDirectory(prefix='policy-determinism-', dir=Path(ctx['project_root'])/'artifacts') as temp:
        root = Path(temp)
        for name in ('one', 'two'):
            build(api, protocol, template, baseline, blueprint_path, requirements_path, root/(name+'.zip'))
        first, second = digest(root/'one.zip'), digest(root/'two.zip')
    return {'schemaVersion': api['SCHEMA_VERSION'], 'status': 'PASS' if first == second else 'FAIL',
            'firstSha256': first, 'secondSha256': second, 'identical': first == second}


def canonical(entity, field, value, protocol):
    if value and entity['types'].get(field) == 'date':
        return rate_date(value, field).isoformat()
    return value


def reconcile(api, protocol, baseline, candidate_path, blueprint_path, requirements_path, export_path, historical_proof=None):
    blueprint = api['_read_json'](blueprint_path); requirements = api['_read_json'](requirements_path)
    if not isinstance(blueprint, dict) or not isinstance(requirements, list):
        raise ValueError('Blueprint and requirements must use the declared object/list shapes')
    if historical_proof is None:
        ctx, review = checked(api, protocol, baseline, blueprint, requirements)
        historical = None
    else:
        from historical_verification import verify
        ctx, historical = verify(api, protocol, baseline, candidate_path, blueprint_path, requirements_path, historical_proof)
        review = {'candidate_sha256': digest(candidate_path)}
    for path in (baseline, candidate_path, export_path):
        package = api['_read_package'](path, protocol)
        if not same_environment(package.metadata['ProcessEnv'], ctx['environment']):
            raise ValueError('Reconciliation export environment differs from the bound preparation')
    if digest(candidate_path) != review['candidate_sha256']:
        raise ValueError('Reconciliation candidate is not the validated ordinary preparation')
    verify_submission_metadata(baseline, candidate_path)
    before, submitted, persisted = [rows(p) for p in (baseline, candidate_path, export_path)]
    entities = {e['name']: e for e in protocol['package']['entities']}
    runtime = json.loads(Path(ctx['runtime_contract']).read_text())
    def key(name, row):
        return tuple(canonical(entities[name], f, row.get(f, ''), protocol)
                     for f in runtime['entities'][name]['identity_fields'])
    # No inferred IDs for preservation-only entities. Compare complete non-audit
    # row multisets, preserving duplicates and allowing concurrent unrelated inserts.
    touched = {(op['entity'], key(op['entity'], op['targetKey'])) for op in blueprint['operations']}
    preservation = []
    for name, entity in entities.items():
        fields = [f for f in entity['headers'] if f not in entity['auditFields']]
        def protected(row):
            return name not in runtime['entities'] or (name, key(name, row)) not in touched
        def counts(source):
            return Counter(tuple(canonical(entity, f, row[f], protocol) for f in fields)
                           for row in source[name] if protected(row))
        missing = counts(before) - counts(persisted)
        preservation.append({'entity': name, 'passed': not missing,
            'missingBaselineRows': sum(missing.values()), 'comparison': 'non-audit row multiset; no invented business identity'})
    matrix = []
    for req in requirements:
        name = req['entity']; entity = entities[name]; wanted = key(name, req['targetKey'])
        left = [row for row in before[name] if key(name, row) == wanted]
        cand = [row for row in submitted[name] if key(name, row) == wanted]
        right = [row for row in persisted[name] if key(name, row) == wanted]
        passed = len(cand) == len(right) == 1
        differences = []
        if req['kind'] == 'value' and passed:
            f = req['field']; expected = canonical(entity, f, req['requestedValue'], protocol)
            passed = all(canonical(entity, f, r[f], protocol) == expected for r in (cand[0], right[0]))
        elif req['kind'] == 'preserve_target' and passed:
            op = next(op for op in blueprint['operations'] if op['id'] == req['operationId'])
            fields = set(entity['headers']) - set(op['values']) - set(entity['auditFields'])
            passed = len(left) == 1
            if passed:
                differences = [f for f in fields if canonical(entity, f, left[0][f], protocol) != canonical(entity, f, right[0][f], protocol)]
                passed = not differences
        elif req['kind'] == 'preserve_rows':
            passed = all(item['passed'] for item in preservation)
        matrix.append({'requirementId': req['id'], 'requirement': req['requirement'],
            'passed': passed, 'detail': differences,
            'candidate': cand, 'persisted': right, 'requested': req.get('requestedValue', 'record/preservation')})
    metadata = compare(baseline, export_path, entities, protocol['package'].get('nodeSequencePolicy'))
    clean = all(r['passed'] for r in matrix) and metadata['compatible']
    return {'schemaVersion': api['SCHEMA_VERSION'], 'status': 'PASS' if clean else 'FAIL',
        'requirementMatrix': matrix, 'preservation': preservation, 'metadata': metadata,
        'baselineSha256': digest(baseline), 'candidateSha256': digest(candidate_path),
        'exportSha256': digest(export_path), 'mismatchCount': sum(not r['passed'] for r in matrix) + int(not metadata['compatible']),
        'historicalVerification': historical,
        'importApproved': False, 'liveQualification': 'Only a real independently captured fresh export can qualify persistence.'}


def rollback(*args):
    raise ValueError('Policies reverse updates/cleanup require separately bound workbook and reference evidence; no automatic rollback or deletion is qualified')
