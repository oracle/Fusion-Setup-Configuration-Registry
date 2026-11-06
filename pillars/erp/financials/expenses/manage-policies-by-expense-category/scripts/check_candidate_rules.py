"""Evaluate ordinary Meals rules for the exact final ZIP before native preview.

Called only at Task Hook's planned read-only evaluation step. No native envelope,
waiver, approval, upload or Fusion request is constructed by this helper.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from build_fsm_from_workbook import candidate, ensure_task_plan
from workbook_intake import ROOT

RESOURCES = ['ora_input_validation.md','ora_reference_lookups.md',
    'ora_dependency_readiness.md','ora_defaulting_rules.md','ora_design_enforcement.md']


def evaluate(workbook, baseline, contract, artifact, **context):
    ensure_task_plan()
    review = candidate(workbook,baseline,contract,None,dry_run=True,**context)
    if review.get('native_preflight_ready') is not True or review.get('trial_admission') is not None:
        raise ValueError('Ordinary supported Meals profile required; no trial readiness override')
    path = Path(artifact)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Final native upload artifact is missing or unsafe')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != review['candidate_sha256']:
        raise ValueError('Final upload artifact differs from the exact reviewed workbook/baseline candidate')
    pending = review['accepted_profile'].get('requires_live_qualification') is True
    return {'command':'rules','candidate_sha256':digest,'profile':review['accepted_profile'],
        'ruleResults':[{'source':source,'status':'passed',
            'issues':[{'severity':'warning','message':'Meals settings, batch/effective-date combinations or the selected target still require live reconciliation. Native approval authorizes an attempt, not a guaranteed outcome or batch atomicity.'}]
                if pending and source=='ora_input_validation.md' else [],'changes':[],
            'sourceSha256':hashlib.sha256((ROOT/'ora-resource'/source).read_bytes()).hexdigest()}
            for source in RESOURCES],
        'qualification_notice':('Settings, batch/effective-date combinations or selected target passed local validation but still need live reconciliation; disclose before native approval.' if pending
            else 'Accepted core profile; native approval and per-run reconciliation remain required.'),
        'authority_boundary':'Read-only task evaluation only. Use native Task Hook preview/approval and Data Loader; never reuse after artifact/context changes.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['workbook','baseline-zip','candidate-zip','baseline-receipt','baseline-export-plan',
                 'baseline-export-approval','currency-receipt']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--runtime-contract',type=Path,default=ROOT/'references/fsm-runtime-contract.json')
    parser.add_argument('--project-root',type=Path)
    for name in ['environment','baseline-process-id','target-origin','validation-date']:
        parser.add_argument('--'+name,required=True)
    args = parser.parse_args()
    result = evaluate(args.workbook,args.baseline_zip,args.runtime_contract,args.candidate_zip,
        expected_environment=args.environment,expected_process_id=args.baseline_process_id,
        baseline_receipt=args.baseline_receipt,baseline_export_plan=args.baseline_export_plan,
        baseline_export_approval=args.baseline_export_approval,currency_receipt=args.currency_receipt,
        target_origin=args.target_origin,validation_date=args.validation_date,project_root=args.project_root)
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError,OSError,KeyError) as error:
        print(json.dumps({'status':'blocked','stage':'task_rule_evaluation',
            'failure_class':'input_validation','message':str(error),'import_approved':False}))
        sys.exit(2)
