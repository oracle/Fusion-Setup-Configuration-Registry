#!/usr/bin/env python3
"""Run Time Slots through the shared Field Service workflow."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
SHARED=Path(__file__).resolve().parents[3]/'scripts';sys.path.insert(0,str(SHARED))
from task_orchestration import WorkflowBlocked,run
from task_adapter import TimeSlotsAdapter
ROOT=Path(__file__).resolve().parents[6]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workbook',required=True,type=Path);p.add_argument('--execution-direction',choices=('ora_rest_execution','core.data-loader.task-rest'));p.add_argument('--mode',choices=('preview','execute'),default='preview');p.add_argument('--approve-checksum');p.add_argument('--include-exact-preview',action='store_true',help='Return the exact preview to the caller in preview mode; durable evidence remains redacted.');p.add_argument('--properties',type=Path,default=ROOT/'core/auth/fusionEnv.properties');p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 try:
  if a.include_exact_preview and a.mode!='preview':raise WorkflowBlocked('--include-exact-preview is available only in preview mode.')
  result=run(TimeSlotsAdapter(),a.workbook,a.execution_direction,a.mode,a.approve_checksum,a.properties,a.output,include_exact_preview=a.include_exact_preview)
  print(json.dumps(result,sort_keys=True))
  return 0 if result.get('status') in {'completed','no_changes','approval_required'} else 2
 except (OSError,ValueError,WorkflowBlocked,RuntimeError) as e:print(f'Time Slots workflow blocked: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
