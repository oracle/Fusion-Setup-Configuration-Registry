"""Build a baseline-preserving policy FSM candidate using reviewed field contracts."""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
import re
import subprocess
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from workbook_intake import ROOT, TASK, IntakeError, artifact_output, checked_zip, csv_bytes, load_catalog, read_package, read_workbook, sha256, xml
from category_scope import require_scoped_records, require_target_rate_identities
from no_default_inputs import enforce_no_default_inputs
from reference_gate import require_qualified_reference_route
import baseline_evidence
from metadata_contract import descriptor
from identity_contract import select_identity
from operation_contract import resolve_policy_operation_contract
from single_currency_policy import policy_constants
from managed_create_fields import managed_create_values


class ContractBlocked(IntakeError):
    pass


def evidence(contract, ids, label):
    sources = contract.get('sources', {})
    if not isinstance(sources,dict):
        sources = {}
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in sources or not sources[i] for i in ids):
        raise ContractBlocked(label+' needs registered evidence')


def field_value(value, rule, spec):
    if spec.get('boolean'):
        mapping = rule.get('value_mapping')
        if not isinstance(mapping, dict) or set(mapping) != {'Yes', 'No'} or any(not isinstance(x, str) for x in mapping.values()):
            raise ContractBlocked('Boolean CSV encoding is unproved')
        result = mapping[value]
    elif spec.get('type') in {'date', 'dateTime'}:
        fmt = rule.get('csv_date_format')
        if fmt not in {'%Y-%m-%d','%Y/%m/%d','%Y-%m-%d %H:%M:%S','%Y/%m/%d %H:%M:%S','%Y-%m-%dT%H:%M:%S'}:
            raise ContractBlocked('Date CSV encoding is unproved')
        result = datetime.fromisoformat(value).strftime(fmt)
    else:
        result = value
    if not isinstance(result, str):
        raise ContractBlocked('Field encoding must produce a text CSV value')
    if 'allowed_values' in rule and result not in rule['allowed_values']:
        raise IntakeError('Value is outside the supported field domain; expected '+repr(rule['allowed_values']))
    maximum = rule.get('max_length')
    if maximum is not None:
        if not isinstance(maximum,int) or maximum < 1 or rule.get('length_unit') not in {'characters','utf8_bytes'}:
            raise ContractBlocked('Invalid length contract')
        size = len(result) if rule['length_unit']=='characters' else len(result.encode('utf-8'))
        if size > maximum:
            raise IntakeError('Value exceeds the verified field length')
    return result


def validate_result(row, entity_contract, contract):
    for rule in entity_contract.get('cross_field_rules', []):
        if not isinstance(rule,dict):
            raise ContractBlocked('Invalid cross-field validation contract')
        if rule.get('kind') in {'nonnegative_decimal', 'strict_decimal_order'}:
            evidence(contract,rule.get('source_ids'),'Numeric cross-field rule')
            fields = [rule.get('field')] if rule['kind']=='nonnegative_decimal' else [rule.get('lower'),rule.get('upper')]
            if any(not isinstance(f,str) or f not in row for f in fields) or len(fields)!=len(set(fields)):
                raise ContractBlocked('Invalid numeric cross-field contract')
            numbers = []
            for field in fields:
                value = row[field]
                if value == '':
                    numbers.append(None)
                    continue
                if not isinstance(value,str) or re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?',value) is None:
                    raise IntakeError(field+': resulting decimal value is invalid')
                try:
                    number = Decimal(value)
                except InvalidOperation:
                    raise IntakeError(field+': resulting decimal value is invalid') from None
                if not number.is_finite():
                    raise IntakeError(field+': resulting decimal value must be finite')
                numbers.append(number)
            if rule['kind']=='nonnegative_decimal':
                if numbers[0] is not None and numbers[0] < 0:
                    raise IntakeError(fields[0]+': resulting value must be nonnegative')
            elif all(n is not None for n in numbers) and numbers[0] >= numbers[1]:
                raise IntakeError(fields[0]+': resulting value must be strictly less than '+fields[1])
            continue
        if rule.get('kind') != 'date_order':
            raise ContractBlocked('Unknown cross-field validation rule')
        evidence(contract,rule.get('source_ids'),'Date cross-field rule')
        start, end = rule.get('start'), rule.get('end')
        if (not isinstance(start,str) or not isinstance(end,str) or start == end
                or start not in row or end not in row):
            raise ContractBlocked('Invalid date cross-field contract')
        formats = entity_contract.get('fields')
        if (not isinstance(formats,dict) or any(not isinstance(formats.get(f),dict)
                or not isinstance(formats[f].get('csv_date_format'),str)
                or formats[f].get('csv_date_format') not in
                {'%Y-%m-%d','%Y/%m/%d','%Y-%m-%d %H:%M:%S','%Y/%m/%d %H:%M:%S','%Y-%m-%dT%H:%M:%S'}
                for f in (start,end))):
            raise ContractBlocked('Date cross-field formats are unqualified')
        if row.get(start) and row.get(end):
            try:
                a=datetime.strptime(row[start],formats[start]['csv_date_format'])
                b=datetime.strptime(row[end],formats[end]['csv_date_format'])
            except (ValueError,KeyError,TypeError):
                raise IntakeError('Resulting date is invalid under the reviewed CSV date format') from None
            if b < a:
                raise IntakeError('Resulting end date precedes start date')


def resolve_policy_resulting_state(row, entity_contract, contract):
    """Apply only the reviewed rule inventory to the complete proposed row."""
    evidence(contract,entity_contract.get('cross_field_source_ids'),'Resulting-state rule inventory')
    if not isinstance(entity_contract.get('cross_field_rules'),list):
        raise ContractBlocked('Explicit resulting-state rule inventory required')
    validate_result(row,entity_contract,contract)


def validate_create_empties(row, entity_contract, contract, entity, input_fields):
    """Blank CSV cells are explicit serialization, never assumed omission."""
    empty = [field for field, value in row.items() if value == '']
    rules = entity_contract.get('create_empty_fields')
    if empty and not isinstance(rules, dict):
        raise ContractBlocked(entity+': explicit-empty create serialization is unproved')
    reviewed = []
    for field in empty:
        rule = rules.get(field)
        if (contract.get('executable_profile') == 'meals-single-currency-v2'
                and entity == 'ORA_EXM_MEALS_POLICY'
                and field in {'RateIncludeMealsFlag','RateIncludeOtherFlag'}
                and isinstance(rule,dict) and rule.get('behavior') == 'observed_server_normalization'
                and rule.get('expected_export_value') == 'N'):
            evidence(contract,rule.get('source_ids'),entity+'.'+field+' accepted server normalization')
            reviewed.append({'field':field,'behavior':rule['behavior'],
                'expected_export_value':'N','source_ids':rule['source_ids']})
            continue
        if not isinstance(rule, dict) or rule.get('behavior') not in {'remains_empty', 'system_generated'}:
            raise ContractBlocked(entity+'.'+field+': explicit-empty create behavior is unproved or defaults a value')
        evidence(contract, rule.get('source_ids'), entity+'.'+field+' create empty')
        if rule['behavior'] == 'system_generated':
            if field in input_fields:
                raise ContractBlocked(entity+'.'+field+': implementor input cannot acquire an automatic generated default')
            field_rule = entity_contract.get('fields', {}).get(field, {})
            if field_rule.get('create') != 'system-managed':
                raise ContractBlocked(entity+'.'+field+': generated-field ownership is unproved')
            evidence(contract, field_rule.get('source_ids'), entity+'.'+field+' generated ownership')
        reviewed.append({'field': field, 'behavior': rule['behavior'], 'source_ids': rule['source_ids']})
    return reviewed


def candidate(workbook, baseline_zip, contract_path, output_dir, *, dry_run=False, expected_environment=None, expected_process_id=None,
              baseline_receipt=None, baseline_export_plan=None, baseline_export_approval=None,
              currency_receipt=None, target_origin=None, validation_date=None, project_root=None):
    catalog=load_catalog()
    model=read_workbook(workbook,catalog)
    if model['status']!='local_shape_valid':
        raise IntakeError('Workbook needs input/correction; no import artifact was created')
    try:
        require_scoped_records(model['records'])
    except ValueError as error:
        raise ContractBlocked(str(error)) from error
    contract=json.loads(Path(contract_path).read_text())
    currency_binding = None
    if currency_receipt is not None:
        from currency_receipt import binding
        currency_binding = binding(workbook, baseline_zip, contract_path,
                                   expected_environment, target_origin, validation_date)
    if contract.get('schema_version')!='1.0' or contract.get('task_code')!=TASK:
        raise ContractBlocked('Runtime contract identity/version mismatch')
    package=contract.get('package')
    if (not isinstance(package,dict)
            or package.get('strategy') not in {'baseline_overlay','sparse_selected_rows'}):
        raise ContractBlocked('Explicit reviewed package submission strategy required')
    evidence(contract,package.get('source_ids'),'Package submission strategy')
    if package['strategy'] != 'sparse_selected_rows':
        raise ContractBlocked('Meals scope requires sparse_selected_rows; whole-baseline submission is not supported')
    sparse=package['strategy']=='sparse_selected_rows'
    if sparse and package.get('unsubmitted_rows')!='preserve':
        raise ContractBlocked('Sparse package requires reviewed unsubmitted-row preservation')
    members, grids=read_package(baseline_zip,catalog)
    baseline_data=Path(baseline_zip).read_bytes()
    with checked_zip(baseline_zip) as archive:
        metadata_member=next(n for n in archive.namelist() if Path(n).name=='ASM_SETUP_CSV_METADATA.xml')
        metadata=xml(archive.read(metadata_member))
        context={x.tag.rsplit('}',1)[-1]:x.text for x in metadata.iter() if x.tag.rsplit('}',1)[-1] in {'ProcessEnv','ProcessId','ProcessRelease'}}
    if expected_environment and context.get('ProcessEnv')!=expected_environment:
        raise IntakeError('Baseline environment mismatch')
    provenance = None
    if expected_process_id is not None or any([baseline_receipt, baseline_export_plan, baseline_export_approval]):
        provenance = baseline_evidence.verify(baseline_zip, baseline_receipt, baseline_export_plan,
                                              baseline_export_approval, expected_environment, expected_process_id)
    if currency_binding is not None:
        from currency_receipt import origin
        if provenance is None or origin(provenance['origin']) != currency_binding['origin']:
            raise ContractBlocked('Currency evidence requires a verified baseline from the same target origin')
    rows={e:[dict(zip(catalog['entities'][e],r)) for r in grid[1:]] for e,grid in grids.items()}
    original_rows = copy.deepcopy(rows)
    accepted_profile = contract.get('executable_profile') is not None
    if accepted_profile:
        ensure_task_plan()
        from accepted_meals_profile import validate_context, validate_selection
        try:
            target_review = validate_context(contract,context,provenance,validation_date,baseline_receipt)
            validate_selection(model['records'],rows)
            supplied_parents = {r['policy_name'] for r in model['records'] if r['entity']=='ORA_EXM_MEALS_POLICY'}
            retained_parents = {r['policy_name'] for r in model['records']} - supplied_parents
            for name in sorted(retained_parents):
                parent = next(r for r in rows['ORA_EXM_MEALS_POLICY']
                    if r['PolicyName']==name)
                require_qualified_reference_route('ORA_EXM_MEALS_POLICY',{},contract['entities']['ORA_EXM_MEALS_POLICY'],
                    currency_context=None if currency_binding is None else {
                        'receipt':currency_receipt,'binding':currency_binding,'policy_name':parent['PolicyName'],
                        'operation':'update','resulting_currency':parent['CurrencyCode']})
        except ValueError as error:
            raise ContractBlocked(str(error)) from error
    try:
        require_target_rate_identities(model['records'], rows)
    except ValueError as error:
        raise ContractBlocked(str(error)) from error
    specs={}
    for sheet in catalog['sheets']:
        for field in sheet['columns']:
            if field['csv_field']:
                specs[sheet['entity'],field['csv_field']]=field
        for alias in sheet.get('shared_entities',[]):
            for field in sheet['columns']:
                if field['csv_field']:
                    specs[alias,field['csv_field']]=field
    changed=set()
    seen=set()
    changes=[]
    selected_rows={e:[] for e in rows}
    parent_context=[]
    for record in sorted(model['records'],key=lambda r:r['kind']!='policy'):
        entity=record['entity']
        if record['unmapped_inputs']:
            raise ContractBlocked('UI-only Policy Start Date has no established CSV mapping')
        current=contract.get('entities',{}).get(entity)
        contract_findings=resolve_policy_operation_contract(entity,current,contract)
        if contract_findings:
            raise ContractBlocked(contract_findings[0]['message'])
        identity=current.get('identity_fields')
        if not isinstance(identity,list) or not identity or len(identity)!=len(set(identity)) or any(f not in catalog['entities'][entity] for f in identity):
            raise ContractBlocked(entity+': invalid portable identity fields')
        match_rule=current.get('identity_match')
        if match_rule not in {'exact','casefold'}:
            raise ContractBlocked(entity+': identity match behavior is unproved')
        def identity_key(row):
            return tuple(row.get(f,'').casefold() if match_rule=='casefold' else row.get(f,'') for f in identity)
        field_rules=current.get('fields',{})
        values={}
        for field,value in record['values'].items():
            if field not in catalog['entities'][entity] or (entity,field) not in specs:
                raise IntakeError('Unmapped or consumer-managed input field')
            rule=field_rules.get(field)
            if not isinstance(rule,dict):
                raise ContractBlocked(entity+'.'+field+': field contract is incomplete')
            evidence(contract,rule.get('source_ids'),entity+'.'+field)
            try:
                values[field]=field_value(value,rule,specs[entity,field])
            except IntakeError as error:
                source = next((s for s in record['sources'] if field in s.get('fields',{})),{})
                location = source.get('sheet',entity)+'!'+source.get('fields',{}).get(field,field)
                raise type(error)(location+': '+str(error)) from error
        nullable=current.get('nullable_identity_fields',[])
        if any(f not in identity for f in nullable):
            raise ContractBlocked('Invalid nullable identity contract')
        if any(f not in values and f not in nullable for f in identity):
            raise IntakeError(entity+': supply every verified identity field')
        key=identity_key(values)
        if (entity,key) in seen:
            raise IntakeError('Multiple workbook references select the same FSM row')
        seen.add((entity,key))
        matches=select_identity(rows[entity],values,identity,match_rule)
        operation='update' if matches else 'create'
        if operation not in current.get('operations',[]):
            raise ContractBlocked(entity+': '+operation+' is not supported by the reviewed contract')
        before=matches[0] if matches else {f:'' for f in catalog['entities'][entity]}
        try:
            constants = policy_constants(entity, operation, before)
        except ValueError as error:
            raise ContractBlocked(str(error)) from error
        for field, value in constants.items():
            rule = field_rules.get(field)
            if not isinstance(rule, dict):
                raise ContractBlocked(entity+'.'+field+': fixed SINGLE mode needs a reviewed field contract')
            evidence(contract, rule.get('source_ids'), entity+'.'+field+' fixed SINGLE mode')
            values[field] = field_value(value, rule, {'type': 'string'})
        try:
            managed_values, managed_review = managed_create_values(entity, operation, current, contract,
                {f for e,f in specs if e==entity})
        except ValueError as error:
            raise ContractBlocked(str(error)) from error
        for field,value in managed_values.items():
            values[field]=field_value(value,field_rules[field],{'type':'string'})
        after=dict(before)
        try:
            currency_review = require_qualified_reference_route(entity,values,current,
                currency_context=None if currency_binding is None else {
                    'receipt': currency_receipt, 'binding': currency_binding,
                    'policy_name': values.get('PolicyName', values.get(entity.removesuffix('_LINE')+'.PolicyName')),
                    'operation': operation, 'resulting_currency': values.get('CurrencyCode',before.get('CurrencyCode'))})
        except ValueError as exc:
            raise ContractBlocked(str(exc)) from exc
        for field,value in values.items():
            if operation=='update' and value==before[field]:
                continue
            if operation=='update' and field=='Status':
                raise ContractBlocked(entity+': status transitions are not qualified by create-status input support')
            if field not in managed_values and field_rules[field].get(operation)!='supported':
                raise ContractBlocked(entity+'.'+field+': '+operation+' acceptance is unproved or unsupported')
            if field in identity and operation=='update':
                raise IntakeError('Identity renames are not supported')
            after[field]=value
        required=current.get('required_fields')
        if not isinstance(required,dict) or not isinstance(required.get(operation),list):
            raise ContractBlocked('Required-field contract is incomplete')
        for field in required[operation]:
            if field not in after or not after[field].strip():
                raise IntakeError(entity+'.'+field+': required resulting value is missing')
        try:
            default_review=enforce_no_default_inputs(entity,operation,values,before)
        except ValueError as exc:
            raise ContractBlocked(str(exc)) from exc
        parent=current.get('parent')
        if sparse and entity.endswith('_LINE'):
            expected_parent=entity[:-5]
            if (not isinstance(parent,dict) or parent.get('entity')!=expected_parent
                    or parent.get('child_field')!=expected_parent+'.PolicyName'
                    or parent.get('parent_field')!='PolicyName'):
                raise ContractBlocked(entity+': sparse rate submission requires its exact owning policy relationship')
        if parent:
            evidence(contract,parent.get('source_ids'),entity+' parent relationship')
            try:
                wanted=after[parent['child_field']]
                parents=[r for r in rows[parent['entity']] if r[parent['parent_field']]==wanted]
            except KeyError:
                raise ContractBlocked('Invalid parent relationship contract') from None
            if not wanted or len(parents)!=1:
                raise IntakeError('Parent policy must resolve to exactly one existing or included policy')
            from reduced_rate_profile import validate_resulting_rate, validate_reduced_parent
            try:
                validate_reduced_parent(parents[0])
                validate_resulting_rate(entity,after,parents[0])
            except ValueError as error:
                raise ContractBlocked(str(error)) from error
            parent_context.append((parent['entity'],parent['parent_field'],wanted))
        if operation=='create':
            status_rule = field_rules.get('Status', {})
            empty_rule = current.get('create_empty_fields', {})
            empty_rule = empty_rule.get('Status', {}) if isinstance(empty_rule, dict) else {}
            consumer_status = managed_values.get('Status') == 'DRAFT'
            if not consumer_status and (status_rule.get('create') != 'system-managed' or empty_rule.get('behavior') != 'system_generated'):
                raise ContractBlocked(entity+': Status is not user-enterable; system-managed create status has not been qualified')
            evidence(contract, status_rule.get('source_ids'), entity+' managed Status ownership')
            if not consumer_status:
                evidence(contract, empty_rule.get('source_ids'), entity+' managed Status serialization')
        if accepted_profile:
            from accepted_meals_profile import validate_change
            try:
                validate_change(entity,operation,before,after,original_rows)
            except ValueError as error:
                raise ContractBlocked(str(error)) from error
        resolve_policy_resulting_state(after,current,contract)
        empty_review = validate_create_empties(after,current,contract,entity,
            {f for e,f in specs if e==entity}) if operation=='create' else []
        selected_rows[entity].append(after)
        if after!=before:
            if matches:
                rows[entity][rows[entity].index(before)]=after
            else:
                rows[entity].append(after)
            changed.add(entity)
            changes.append({'entity':entity,'operation':operation,'sources':record['sources'],
                            'currency_reference_review':currency_review,
                            'create_empty_field_contracts':empty_review,
                            'no_default_input_review':default_review,
                            'skill_constant_review':{'values':constants,'authority':'Explicit user instruction: single currency only; no workbook mode input'},
                            'managed_create_review':managed_review,
                            'fields':[{'field':f,'before':before[f],'after':after[f]} for f in values if before[f]!=after[f]]})
    try:
        require_target_rate_identities(model['records'], rows)
    except ValueError as error:
        raise ContractBlocked(str(error)) from error
    if not changed:
        raise IntakeError('Workbook requests no effective change; no candidate was created')
    context_review=[]
    for entity,field,value in parent_context:
        context_rows=[r for r in rows[entity] if r.get(field)==value]
        if len(context_rows)!=1:
            raise IntakeError('Parent context changed or became ambiguous during preparation')
        row=context_rows[0]
        if row not in selected_rows[entity]:
            selected_rows[entity].append(row)
            context_review.append({'entity':entity,'field':field,'value':value})
    replacement={members[e]:csv_bytes(catalog['entities'][e],selected_rows[e]) for e in rows}
    buffer=io.BytesIO()
    with ZipFile(io.BytesIO(baseline_data)) as source, ZipFile(buffer,'w') as output:
        output.comment=source.comment
        for info in source.infolist():
            output.writestr(info,replacement.get(info.filename,source.read(info.filename)))
    data=buffer.getvalue()
    submitted_records = []
    with ZipFile(io.BytesIO(data)) as archive:
        if archive.read(metadata_member) != descriptor(baseline_zip):
            raise IntakeError('Candidate metadata differs from its bound baseline descriptor')
        for entity,member in members.items():
            grid=list(csv.reader(io.StringIO(archive.read(member).decode('utf-8-sig'))))
            if grid[0]!=catalog['entities'][entity] or any(len(r)!=len(grid[0]) for r in grid[1:]):
                raise IntakeError('Independent candidate row-width verification failed')
            if entity not in {'ORA_EXM_MEALS_POLICY','ORA_EXM_MEALS_POLICY_LINE'} and len(grid)>1:
                raise ContractBlocked('Meals package cannot resubmit unrelated entity rows')
            submitted_records.extend({'entity':entity,'values':dict(zip(grid[0],row)),'shared_entities':[]}
                                     for row in grid[1:])
    # Full submitted rows contain preserved non-input columns. Check identities
    # and counts independently of the input-field allowlist.
    submitted_identities = [{'entity':r['entity'],'values':{
        **({f:r['values'][f] for f in ('StartDate','EndDate')} if r['entity'].endswith('_LINE') else {}),
        ('PolicyName' if r['entity']=='ORA_EXM_MEALS_POLICY' else 'ORA_EXM_MEALS_POLICY.PolicyName'):
        r['values'].get('PolicyName',r['values'].get('ORA_EXM_MEALS_POLICY.PolicyName'))},'shared_entities':[]}
        for r in submitted_records]
    try:
        require_scoped_records(submitted_identities)
    except ValueError as error:
        raise ContractBlocked(str(error)) from error
    profile_review = None
    if accepted_profile:
        from accepted_meals_profile import verify_result
        try:
            profile_review = verify_result(submitted_records,original_rows)
            profile_review['target_qualification'] = target_review
            if target_review['requires_live_qualification']:
                profile_review['requires_live_qualification'] = True
                profile_review['qualification'] = 'selected_target_live_pending'
        except ValueError as error:
            raise ContractBlocked(str(error)) from error
    review={'schema_version':'1.0','task_code':TASK,'status':'locally_validated_candidate','live_qualified':False,
            'baseline_sha256':sha256(baseline_data),'workbook_sha256':model['workbook_sha256'],
            'runtime_contract_sha256':sha256(Path(contract_path).read_bytes()),'candidate_sha256':sha256(data),
            'baseline_context':context,'baseline_provenance':provenance,'changed_entities':sorted(changed),'changes':changes,
            'trial_admission':None,
            'accepted_profile':profile_review,
            'package_submission':{'strategy':package['strategy'],'source_ids':package['source_ids'],
                'submitted_row_counts':{e:len(selected_rows[e]) for e in rows},
                'added_parent_context':context_review,
                'preservation_boundary':'Submission shape only; persisted unsubmitted-row and context/audit effects require fresh reconciliation.'},
            'approval_boundary':'This build does not authorize import. Current rule-plan, Run Book, Task Hook and Data Loader gates remain authoritative.'}
    if accepted_profile:
        review['status']='validated_candidate_for_native_preflight'
        review['import_ready']=False
        review['native_preflight_ready']=True
        review['live_qualified']=not profile_review['requires_live_qualification']
    directory = artifact_output(output_dir, project_root) if output_dir is not None or not dry_run else None
    if not dry_run:
        artifact_output(directory, project_root)
        directory.mkdir(parents=True)
        (directory/'candidate.zip').write_bytes(data)
        (directory/'candidate-build-review.json').write_text(json.dumps(review,indent=2)+'\n')
    return review


def ensure_task_plan():
    planner=ROOT.parent/'scripts/plan_task_rules.py'
    if not planner.is_file():
        raise ContractBlocked('Expenses task rule planner is unavailable')
    command=[sys.executable,str(planner),'--skill-path',str(ROOT),
             '--task-name','Manage Policies by Expense Category','--task-code',TASK]
    try:
        result=subprocess.run(command,text=True,capture_output=True,timeout=60)
    except (OSError,subprocess.TimeoutExpired):
        raise ContractBlocked('Expenses task rule planner could not complete') from None
    if result.returncode:
        raise ContractBlocked('Current task rule plan is blocked; complete the task-owned evidence contracts before candidate construction')
    try:
        plan=json.loads(result.stdout)
        task=plan['plan']['task']
        ready=plan['status']=='planned' and plan['plan']['validation']['status']=='ready'
        identity=task['task_name']=='Manage Policies by Expense Category' and task['task_code']==TASK
    except (ValueError,KeyError,TypeError):
        raise ContractBlocked('Expenses task rule planner returned an invalid plan') from None
    if not ready or not identity:
        raise ContractBlocked('Expenses task rule plan is not ready for this exact task')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook',type=Path,required=True)
    parser.add_argument('--baseline-zip',type=Path,required=True)
    parser.add_argument('--runtime-contract',type=Path,default=ROOT/'references/fsm-runtime-contract.json')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    parser.add_argument('--baseline-process-id',required=True)
    parser.add_argument('--baseline-receipt',type=Path,required=True)
    parser.add_argument('--baseline-export-plan',type=Path,required=True)
    parser.add_argument('--baseline-export-approval',type=Path,required=True)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--currency-receipt',type=Path)
    parser.add_argument('--target-origin')
    parser.add_argument('--validation-date')
    args=parser.parse_args()
    try:
        ensure_task_plan()
        if json.loads(args.runtime_contract.read_text()).get('executable_profile') != 'meals-single-currency-v2':
            raise ContractBlocked('Only the ordinary supported Meals executable profile is accepted by the CLI')
        review=candidate(args.workbook,args.baseline_zip,args.runtime_contract,args.output_dir,dry_run=args.dry_run,
                         expected_environment=args.environment,expected_process_id=args.baseline_process_id,
                         baseline_receipt=args.baseline_receipt, baseline_export_plan=args.baseline_export_plan,
                         baseline_export_approval=args.baseline_export_approval,
                         currency_receipt=args.currency_receipt, target_origin=args.target_origin,
                         validation_date=args.validation_date, project_root=args.project_root)
        print(json.dumps({'status':review['status'],'live_qualified':review['live_qualified'],
            'native_preflight_ready':review.get('native_preflight_ready',False),
            'import_approved':False,'changed_entities':review['changed_entities']}))
        return 0
    except ContractBlocked as exc:
        print(json.dumps({'status':'blocked','failure_class':'catalog_mismatch','message':str(exc)}))
        return 2
    except (IntakeError, OSError, ValueError, KeyError, BadZipFile, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'blocked','failure_class':'input_validation','message':str(exc)}))
        return 2


if __name__=='__main__':
    sys.exit(main())
