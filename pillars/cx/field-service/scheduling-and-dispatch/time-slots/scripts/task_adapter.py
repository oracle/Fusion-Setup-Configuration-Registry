"""Time Slots adapter for the shared Field Service workflow."""
from __future__ import annotations
import importlib.util,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parents[2]/'scripts'))
from task_orchestration import resolve_execution_route
def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/f'{name}.py');module=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(module);return module
PAYLOADS=load('build_time_slots_preview');PREVIEWS=load('build_time_slots_execution_preview')
class TimeSlotsAdapter:
 task_code='ORA_FFS_TS_TIME_SLOTS'
 continue_independent_write_failures=True
 def resolve_route(self,direction:str|None)->dict[str,str]:return resolve_execution_route(ROOT.parent/'ora-resource'/'ora_rest_execution.md',self.task_code,direction)
 def preflight(self,workbook:Path,get:Any,temp:Path):
  payload=PAYLOADS.build_preview_data(workbook);baselines={}
  access=get('/api/field-service/configuration/v1/timeSlots/',temp/'time-slots.json')
  if access is None:raise RuntimeError('Target environment does not expose the Time Slots collection.')
  for sequence,request in enumerate(payload['requests'],1):
   baseline=get(request['path'],temp/f'baseline-{sequence}.json')
   current=baseline or {'state':'not_found','identity':request['identity']}
   baselines[request['identity']]=current
   request['headers']={'FS-IDENTIFY-BY':'label'}
   if current.get('state')=='not_found':request['headers']['If-None-Match']=request['identity']
  for request in payload['requests']:
   baseline=baselines[request['identity']]
   if baseline.get('state')=='not_found':continue
   changed=any(baseline.get(field)!=value for field,value in request['body'].items())
   impact=payload.get('changeImpact',{}).get(request['identity'],'').strip()
   required_terms=('booking','routing','quota','ui','api','validat')
   if changed and (not impact or 'new proposed slot' in impact.casefold() or any(term not in impact.casefold() for term in required_terms)):
    raise ValueError(f"TS.CHANGE_IMPACT: {request['identity']} is an existing changed slot and requires documented booking, routing, quota, UI, API, and validation impact evidence before preview.")
  return payload,baselines
 def build_preview(self,payload,environment,baselines):return PREVIEWS.build_execution_preview(payload,'ora_rest_execution',environment,baselines)
 def mismatches(self,expected:dict[str,Any],actual:dict[str,Any])->list[str]:
  return [key for key,value in expected.items() if actual.get(key)!=value]
