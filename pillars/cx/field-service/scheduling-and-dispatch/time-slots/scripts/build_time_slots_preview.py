#!/usr/bin/env python3
"""Build implementation Time Slots create/update PUT candidates from XLSX."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from guarded_xlsx import GuardedWorkbook, column_index, shared_string

class PreviewInputError(ValueError): pass
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"; REL="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"; PKG="{http://schemas.openxmlformats.org/package/2006/relationships}"
ALIASES={"id":("id",),"label":("time slot label","label"),"name":("name","time slot name"),"status":("status",),"all_day":("all-day","all day","all_day"),"start":("start time","time start","timefrom"),"end":("end time","time end","timeto"),"business_purpose":("business purpose",),"booking_model":("booking model",),"eligible_activity_types":("eligible activity types",),"change_impact":("change impact",),"activity_types":("activity types",),"capacity_categories":("capacity categories",),"warehouse_visits":("warehouse visits",)}
def norm(v:Any)->str:return " ".join(str(v or "").replace("\xa0"," ").strip().rstrip("*").strip().split()).casefold()
col = column_index
def _strings(z):
 try:return [''.join(x.itertext()) for x in z.xml('xl/sharedStrings.xml').findall(f'{NS}si')]
 except KeyError:return []
def read_rows(path:Path)->list[list[Any]]:
 try:
  with GuardedWorkbook(path) as z:
   wb=z.xml('xl/workbook.xml');rels=z.xml('xl/_rels/workbook.xml.rels');targets={x.attrib['Id']:x.attrib['Target'] for x in rels.findall(f'{PKG}Relationship')};ss=_strings(z)
   sheet=next((s for s in wb.findall(f'{NS}sheets/{NS}sheet') if norm(s.attrib.get('name'))=='time slots'),None)
   if sheet is None:raise PreviewInputError('No Time Slots worksheet was found.')
   target=targets[sheet.attrib[f'{REL}id']].lstrip('/')
   sheet_path=target if target.startswith('xl/') else 'xl/'+target
   root=z.xml(sheet_path);out=[]
   z.check_time()
   for r in root.findall(f'{NS}sheetData/{NS}row'):
    z.check_time()
    values={}
    for c in r.findall(f'{NS}c'):
     v=c.find(f'{NS}v');typ=c.attrib.get('t');value=None if v is None else v.text
     if typ=='s' and value is not None:value=shared_string(ss,value)
     elif typ=='inlineStr':value=''.join(c.itertext())
     values[col(c.attrib.get('r',''))]=value
    out.append([values.get(i) for i in range(1,max(values,default=0)+1)])
   return out
 except PreviewInputError:raise
 except Exception as e:raise PreviewInputError(f'Workbook could not be read: {e}') from e
def header(rows):
 for i,row in enumerate(rows):
  found={}
  for j,v in enumerate(row):
   for field,names in ALIASES.items():
    if norm(v) in names:found[field]=j
  if {'label','status','start','end'}<=set(found):return i,found
 raise PreviewInputError('Time Slots headers must include Time Slot Label, Status, Start Time, and End Time.')
def value(row,ix,key):return row[ix[key]] if key in ix and ix[key]<len(row) else None
def boolean(v,field):
 x=norm(v)
 if x in {'true','yes','y','1','active','enabled'}:return True
 if x in {'false','no','n','0','inactive','disabled',''}:return False
 raise PreviewInputError(f'{field} must be an unambiguous boolean.')
def as_time(v,field):
 raw=str(v or '').strip()
 try:
  n=float(raw)
  if 0<=n<1:m=round(n*1440);return f'{m//60:02d}:{m%60:02d}'
 except ValueError:pass
 match=re.fullmatch(r'(\d{1,2}):(\d{2})(?:\s*([AaPp][Mm]))?',raw)
 if not match:raise PreviewInputError(f'{field} must be an Excel time or HH:MM value.')
 h,m=int(match.group(1)),int(match.group(2));ampm=match.group(3)
 if m>59 or (ampm and not 1<=h<=12) or (not ampm and h>23):raise PreviewInputError(f'{field} is outside the 24-hour clock.')
 if ampm:h=(h%12)+(12 if ampm.casefold()=='pm' else 0)
 return f'{h:02d}:{m:02d}'
def split(v):return [x.strip() for x in re.split(r'[;,\n]+',str(v or '')) if x.strip()]
def design_error(rownum:int,rule:str,message:str)->PreviewInputError:return PreviewInputError(f'Row {rownum}: {rule}: {message}')
def _purpose(value:Any)->str:
 return ' '.join(str(value or '').split()).strip()
def _duration(start:str,end:str)->int:
 return (int(end[:2])*60+int(end[3:]))-(int(start[:2])*60+int(start[3:]))
def _overlap(left:dict[str,Any],right:dict[str,Any])->bool:
 return left['start']<right['end'] and right['start']<left['end']
def validate_design_rules(records:list[dict[str,Any]])->None:
 """Apply the local TS.* design rules before a REST preview is permitted."""
 quota=[]
 for record in records:
  rownum,label,purpose=record['rownum'],record['label'],record['businessPurpose']
  if not purpose or norm(purpose) in {'required','standard','default','n/a','na'}:raise design_error(rownum,'TS.BUSINESS_PURPOSE','Business Purpose must document a row-specific operating purpose.')
  if not re.fullmatch(r'\d{2}-\d{2}',label):raise design_error(rownum,'TS.NAMING_AND_STATUS','Time Slot Label must use the sortable HH-HH convention, for example 08-10.')
  if label != f"{record['start'][:2]}-{record['end'][:2]}":raise design_error(rownum,'TS.NAMING_AND_STATUS','Time Slot Label must match the bounded Start Time and End Time.')
  if not record['active'] and re.search(r'customer|booking|routing|assignment|quota|api|ui',purpose,re.I):raise design_error(rownum,'TS.NAMING_AND_STATUS','A slot required by its documented purpose must be Active.')
  for activity_type in record['eligibleActivityTypes']:
   if norm(activity_type).rstrip('s') not in norm(purpose):raise design_error(rownum,'TS.ACTIVITY_TYPE_ELIGIBILITY',f'Business Purpose must explain why {activity_type!r} is eligible in this slot.')
  model=record['bookingModel']
  if model not in {'','none','quota-based','availability-based'}:raise design_error(rownum,'TS.QUOTA_DESIGN','Booking Model must be None, Quota-based, or Availability-based.')
  if model=='quota-based':
   match=re.search(r'typical activity(?:\s+is|\s*:)\s*(\d+)\s*minutes',purpose,re.I)
   if not match or 'capacity categor' not in purpose.casefold():raise design_error(rownum,'TS.QUOTA_DESIGN','Quota-based slots require typical activity duration and capacity-category alignment evidence.')
   if _duration(record['start'],record['end'])<int(match.group(1)):raise design_error(rownum,'TS.QUOTA_DESIGN','The slot is shorter than the documented typical activity.')
   quota.append(record)
  if model=='availability-based' and not all(term in purpose.casefold() for term in ('service level','booking effect')):raise design_error(rownum,'TS.AVAILABILITY_DESIGN','Availability-based slots require service-level and booking-effect evidence.')
 for index,left in enumerate(quota):
  for right in quota[index+1:]:
   if _overlap(left,right):raise design_error(right['rownum'],'TS.QUOTA_DESIGN',f'Quota-based slot intersects {left["label"]}.')
def build_preview_data(workbook_path:Path)->dict[str,Any]:
 if not workbook_path.is_file() or workbook_path.suffix.casefold()!='.xlsx':raise PreviewInputError('workbook must be an existing .xlsx file.')
 allrows=read_rows(workbook_path);first,ix=header(allrows)
 if 'business_purpose' not in ix:raise PreviewInputError('Time Slots headers must include Business Purpose.')
 requests=[];records=[];labels=set()
 for rownum,row in enumerate(allrows[first+1:],first+2):
  if 'id' in ix and not norm(value(row,ix,'id')):continue
  label=str(value(row,ix,'label') or '').strip()
  if not label:continue
  if label in labels:raise PreviewInputError(f'Row {rownum}: Time Slot Label values must be unique.')
  labels.add(label);active=boolean(value(row,ix,'status'),'Status');name=str(value(row,ix,'name') or label).strip() or label
  if 'all_day' in ix and boolean(value(row,ix,'all_day'),'All-day'):
   raise PreviewInputError(f'Row {rownum}: All-day has no documented writable Time Slots payload mapping.')
  start=as_time(value(row,ix,'start'),'Start Time');end=as_time(value(row,ix,'end'),'End Time')
  if start>=end:raise PreviewInputError(f'Row {rownum}: End Time must be after Start Time.')
  if norm(value(row,ix,'warehouse_visits')):raise PreviewInputError(f'Row {rownum}: Warehouse Visits has no implementation Time Slots payload mapping.')
  body={'label':label,'name':name,'active':active,'timeStart':start,'timeEnd':end}
  path=f'/api/field-service/configuration/v1/timeSlots/{quote(label,safe="")}';requests.append({'operationId':'put-time-slot','identity':label,'method':'PUT','path':path,'expectedStatuses':[200,201],'body':body})
  records.append({'rownum':rownum,'label':label,'active':active,'start':start,'end':end,'businessPurpose':_purpose(value(row,ix,'business_purpose')),'bookingModel':norm(value(row,ix,'booking_model')),'eligibleActivityTypes':split(value(row,ix,'eligible_activity_types'))})
 if not requests:raise PreviewInputError('No Time Slots records with a Time Slot Label were found.')
 validate_design_rules(records)
 return {'operation':'create-or-update','requests':requests,'designEvidence':records,'changeImpact':{record['label']:_purpose(value(allrows[record['rownum']-1],ix,'change_impact')) for record in records}}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workbook',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 try:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(build_preview_data(a.workbook),indent=2,sort_keys=True)+'\n');return 0
 except PreviewInputError as e:print(f'Input validation: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
