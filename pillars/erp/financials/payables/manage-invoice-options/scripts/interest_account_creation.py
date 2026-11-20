#!/usr/bin/env python3
"""Prepare or execute separately approved interest-account creation, then revalidate.

The ordinary resolver always uses DynamicInsertion=No. This explicit command
rechecks absence/configuration and uses its task-owned approval adapter.
"""
from __future__ import annotations
import argparse
from functools import partial
import importlib.util
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interest_account_validation as validation
from interest_account_resolution import diagnose_account, lookup_account, classify_account, ResolutionError
import resolve_lookup_prerequisites as resolver
from fsm_task_adapter import _interest_account_context, _load_contract, _read_package, _validate_new_outputs, AdapterError
import data_loader_metadata as metadata


def workflow():
    path = Path(__file__).resolve().with_name('account_combination_workflow.py')
    if not path.is_file():
        raise ResolutionError('Invoice Options account approval adapter is unavailable. Install the complete Invoice Options skill.')
    spec = importlib.util.spec_from_file_location('invoice_account_approval_workflow', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def creation_envelope(ledger: str, segments: list[str]) -> bytes:
    # Preserve each supplied slot, including blanks. Fusion owns requiredness
    # and segment-value validation; approval still binds the exact request.
    root = ElementTree.fromstring(validation.build_envelope(ledger_name=ledger, segments=segments))
    node = root.find('.//{' + validation.SERVICE_NAMESPACE + '}DynamicInsertion')
    # The service's creating wire flag is Y; the workflow's logical mode is Yes.
    node.text = 'Y'
    row = root.find('.//{' + validation.TYPES_NAMESPACE + '}validationInputRowList')
    ElementTree.SubElement(row, '{' + validation.SERVICE_NAMESPACE + '}EnabledFlag').text = 'true'
    return ElementTree.tostring(root, encoding='utf-8', xml_declaration=True)


def _creation_summary(content: bytes, *, http_status: int):
    result = validation.response_summary(content, http_status=http_status)
    return {**result,'readOnly':False,'dynamicInsertion':'Yes'}


def prepare(args):
    design = resolver._read_json(args.design)
    ops = design.get('operations', [])
    selected = [op for op in ops if not args.operation_id or op.get('id') == args.operation_id]
    if len(selected) != 1:
        raise ResolutionError('Select exactly one Invoice Options operation for account creation.')
    op = selected[0]
    config = metadata.read_config(args.properties, **metadata.oauth_kwargs(args))
    config['coaConfiguration'] = args.coa_configuration
    baseline = _read_package(args.baseline, _load_contract(resolver.TASK_ROOT/'e2e-adapter.json'))
    # Verify the independent selected environment/origin before any account call.
    resolver._configured_reference_target(config, design.get('referenceContext'), baseline)
    context = _interest_account_context(design, {'name':'AP_SYSTEM_PARAMETER','keyFields':['BuName']}, op, baseline)
    if context is None:
        raise ResolutionError('This operation does not request an interest account requiring validation.')
    account, ledger = context
    proof, instance, chart = lookup_account(config, baseline, ledger, account)
    if proof['exactMatches']:
        raise ResolutionError('This account already exists. Rerun ordinary validation; creation is unnecessary.')
    decision = classify_account(proof, instance, chart, {})
    if decision.get('creationAllowed') is not True:
        raise ResolutionError(decision['message'])
    segments = validation.parse_segments(account)
    envelope = creation_envelope(ledger, segments)
    binding = {'operationId':op['id'],'targetKey':op['targetKey'],'baselineSha256':baseline.archive_sha256,
               'configurationSha256':decision['configurationSha256']}
    return config, ledger, account, envelope, binding, decision


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--design',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--coa-configuration',type=Path,required=True)
    parser.add_argument('--operation-id')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preview-output',type=Path)
    mode.add_argument('--approval-file',type=Path)
    mode.add_argument('--decline',action='store_true')
    parser.add_argument('--output',type=Path)
    metadata.add_oauth_arguments(parser)
    args = parser.parse_args(argv)
    creation_returned = False
    try:
        if args.decline:
            if args.output:
                raise ResolutionError('Decline does not submit or write a creation receipt.')
            print(json.dumps({'status':'DECLINED','accountCreated':False,'setupChanged':False,
                'message':'No account was created. Choose an existing account or stop.'}))
            return 0
        if bool(args.approval_file) != bool(args.output):
            raise ResolutionError('--approval-file requires a new --output execution receipt; preview uses --preview-output alone.')
        protected = [args.design,args.baseline,args.coa_configuration,args.properties]
        if args.approval_file:
            protected.append(args.approval_file)
        _validate_new_outputs([args.output or args.preview_output],protected)
        revalidation_output = (args.output.with_name(args.output.stem + '-revalidation.json')
                               if args.output else None)
        if revalidation_output:
            _validate_new_outputs([revalidation_output], protected + [args.output])
        deferral_output = (args.output.with_name(args.output.stem + '-fsm-deferral.json') if args.output else None)
        if deferral_output:
            _validate_new_outputs([deferral_output], protected + [args.output, revalidation_output])
        rejection_output = (args.output.with_name(args.output.stem + '-rejection.json') if args.output else None)
        if rejection_output:
            _validate_new_outputs([rejection_output], protected + [args.output, revalidation_output, deferral_output])
        control = workflow()
        config,ledger,account,envelope,binding,decision = prepare(args)
        props = config['auth'].properties
        request = control.request_context(props, endpoint=validation.SERVICE_PATH,
            soap_action=validation.VALIDATE_SOAP_ACTION, operation='validateAndCreateAccounts',
            envelope=envelope,read_only=False,business_context={'ledgerName':ledger,'segments':validation.parse_segments(account),'dynamicInsertion':'Yes'})
        if args.preview_output:
            preview = {'schemaVersion':'fscr-soap-preview-v1','request':request,'taskContext':binding,
                'creationAttributes': {'DynamicInsertionWireValue': 'Y', 'EnabledFlag': True},
                'accountResolution':decision,'message':'Approve creation of this exact account combination. Created GL accounts remain if the later Invoice Options import is cancelled or fails. Invoice Options will not be saved by this command.'}
            control.write_new_json(args.preview_output,preview,protected_inputs=protected)
            print(json.dumps({'status':'AWAITING_APPROVAL','preview':str(args.preview_output),'request':request,'taskContext':binding,'message':preview['message']}))
            return 0
        approval = resolver._read_json(args.approval_file)
        if approval.get('taskContext') != binding:
            raise ResolutionError('Creation approval does not match this operation, BU, baseline and COA configuration.')
        # The task-owned workflow checks request approval, reserves the receipt,
        # records dispatch, and submits exactly once without mutation retries.
        result = control.execute(props,endpoint=validation.SERVICE_PATH,soap_action=validation.VALIDATE_SOAP_ACTION,
            operation='validateAndCreateAccounts',envelope=envelope,read_only=False,
            business_context=request['businessContext'],summarize=_creation_summary,output=args.output,
            approval=approval,protected_inputs=protected,token_cache=args.token_cache,force_login=args.force_login,
            open_browser=args.open_browser,callback_timeout=args.callback_timeout)
        creation_returned = True
        if not result.get('valid'):
            from interest_account_fsm_fallback import eligible_creation_failure, make_deferral
            if eligible_creation_failure(result):
                # A business rejection is not absence proof. Reconcile with fresh lookup.
                baseline = _read_package(args.baseline, _load_contract(resolver.TASK_ROOT/'e2e-adapter.json'))
                proof, instance, chart = lookup_account(config, baseline, ledger, account)
                current = classify_account(proof, instance, chart, {})
                op = next(op for op in resolver._read_json(args.design)['operations'] if op['id'] == binding['operationId'])
                provenance = resolver._new_reference_provenance(
                    resolver._read_json(args.design).get('referenceContext'), baseline)
                deferred = make_deferral(result, current, binding, operation=op, account=account,
                                         ledger=ledger, provenance=provenance)
                control.write_new_json(deferral_output, deferred, protected_inputs=protected + [args.output])
                print(json.dumps({'status':'DEFERRED_TO_FSM','receipt':str(args.output),
                    'deferral':str(deferral_output),'accountCreated':False,'setupChanged':False,
                    'message':'This combination will be submitted for creation with the Invoice Options import, subject to its exact preview and approval.'}))
                return 2
            from interest_account_override import business_rejection
            if business_rejection(result):
                rejected = {'schemaVersion': 'invoice-account-creation-rejection-v1',
                    'creationReceipt': result, 'taskContext': binding}
                control.write_new_json(rejection_output, rejected, protected_inputs=protected + [args.output])
            print(json.dumps({'status':'CREATION_REJECTED','receipt':str(args.output),
                'accountValidation':result.get('validationFailure'),'mayHaveApplied':result['mayHaveApplied'],
                'message':'Creation did not return a valid account. Keep the receipt and reconcile before another approved attempt.'}),file=sys.stderr)
            return 1
        recheck = resolver._run_account_validation(config,ledger,account)
        control.write_new_json(revalidation_output, recheck, protected_inputs=protected + [args.output])
        created_id = result.get('responseFields',{}).get('CcId')
        if recheck.get('valid') is not True or recheck.get('responseFields',{}).get('CcId') != created_id:
            print(json.dumps({'status':'REVALIDATION_FAILED','receipt':str(args.output),'mayHaveApplied':True,
                'message':'Creation returned an account, but read-only revalidation did not confirm the same usable CCID. Invoice Options remains blocked.'}),file=sys.stderr)
            return 1
        print(json.dumps({'status':'CREATED_AND_REVALIDATED','receipt':str(args.output),'ccid':created_id[0],
            'setupChanged':False,'message':'The account is usable. Rerun the ordinary lookup resolver to obtain a fresh bound receipt, then continue the normal Invoice Options preview and approval.'}))
        return 0
    except (ResolutionError,AdapterError,resolver.LookupPreflightError,metadata.DataLoadError,OSError,ValueError,RuntimeError) as exc:
        print(json.dumps({'status':'FAIL','failureClass':getattr(exc,'failure_class','input_validation'),
            'mayHaveApplied':creation_returned or getattr(exc,'may_have_applied',False),'error':str(exc)}),file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
