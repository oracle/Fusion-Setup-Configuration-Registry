// Rebuild the authorized reduced intake from its task-owned catalog.
// Run with the bundled artifact-tool runtime; no network operations.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const task=path.resolve('pillars/erp/financials/expenses/manage-policies-by-expense-category');
const output=process.argv[2] ?? path.join(task,'assets/ManagePoliciesByExpenseCategory_Input.xlsx');
const previews=process.argv[3];
const catalog=JSON.parse(await fs.readFile(path.join(task,'references/intake-fields.json'),'utf8'));
const wb=Workbook.create();
const letter=n=>{let r='';for(;n;n=Math.floor((n-1)/26))r=String.fromCharCode(65+(n-1)%26)+r;return r;};
const base=sheet=>{sheet.showGridLines=true;sheet.getRange('A1:P205').format.font={name:'Arial',size:11};};
const title=(sheet,text,last)=>{
  sheet.getRange(`A1:${last}1`).merge();sheet.getRange('A1').values=[[text]];
  sheet.getRange(`A1:${last}1`).format={fill:'#595959',font:{name:'Arial',size:16,bold:true,color:'#FFFFFF'},rowHeight:32};
};
const start=wb.worksheets.add('Start Here');base(start);title(start,'Manage Policies by Expense Category','B');
start.getRange('A1:A24').format.columnWidth=27;start.getRange('B1:B24').format.columnWidth=105;
const instructions=[
 ['Category','Meals policies and rates only. All other expense categories are outside this workbook.'],
 ['Enter values','Supply multiple Meals policies and multiple rates per policy. Use one row per policy and one row per rate. Repeat the exact Policy Name on each associated rate.'],
 ['Blank cells','Blank cells do not result in clearing existing value on an environment or automatic value defaulting.'],
 ['Rate currency','Single currency only. Enter a currency code enabled and active in your environment, such as USD, EUR or GBP. The skill fixes mode SINGLE. Existing policy currencies cannot be changed.'],
 ['Rate determinants','Role and location are not user inputs. Each selected policy must not require them. Existing sibling rates are validated; unrelated setup is preserved.'],
 ['Meals limits','Enable Single Instance Limit, Daily Sum Limit or both. Supply every enabled rate amount. Leave disabled amounts blank. Blank updates preserve saved values; disabling a populated limit is unsupported.'],
 ['Policy Enforcement','Choose Reimburse upper limit when expense exceeds defined rate or Generate policy violation when expense exceeds defined rate.'],
 ['Dates','Use Excel dates or YYYY-MM-DD. Supply End Date for bounded periods; blank means open-ended. Periods for one policy must not overlap (end dates inclusive). Reuse exact Start/End Date keys for updates.'],
 ['Removed inputs','Rates source, meal inclusion, geography, zones, seasonal rates, gender, rate type and all Status fields are not user inputs.'],
 ['Warning controls','Under violation enforcement, Warning Tolerance is required when Policy Violation Warning is Yes. Error Tolerance is required when Prevent Report Submission is Yes. If both are present, warning must be less than error.'],
 ['Enforcement controls','Reimburse upper limit requires warning, display and prevention controls No. Display Warning to User Yes requires Policy Violation Warning Yes. Blank updates preserve stored tolerances.'],
 ['New records','Supply each new policy with at least one rate. Add nonoverlapping rates or update exact existing keys. No automatic closing/deleting rates. Draft status is managed. Batches and End Date require live verification.'],
];
for(let i=0;i<instructions.length;i++){
 const row=i*2+3;start.getRange(`A${row}:B${row}`).values=[instructions[i]];
 start.getRange(`A${row}`).format.font={bold:true};start.getRange(`B${row}`).format.wrapText=true;
 start.getRange(`A${row}:B${row}`).format.rowHeight=42;
}
const notes=(sheet,field)=>{
 if(field.workbook_only)return 'Always Yes for this category. Prefilled display indicator only; no separate FSM parent flag is written.';
 if(field.csv_field.endsWith('.PolicyName'))return 'Repeat the exact Policy Name from the parent sheet. This is an association, not an Oracle ID.';
 if(field.csv_field==='SingleInstanceLimit')return 'Supply when Single Instance Limit? on Meals is Yes. Otherwise leave blank. Amounts use the parent policy currency.';
 if(field.csv_field==='DailyLimit')return sheet.entity==='ORA_EXM_MEALS_POLICY_LINE'?'Supply when Daily Sum Limit? on Meals is Yes. Otherwise leave blank. Amounts use the parent policy currency.':'Daily monetary limit in the parent policy currency.';
 if(field.csv_field==='EndDate')return 'Optional inclusive end of this period. Leave blank only for an open-ended period. On updates supply the exact existing End Date key; key changes are unsupported. Periods must not overlap.';
 if(field.csv_field==='CurrencyCode')return 'Enter an enabled, active parent currency code, such as USD, EUR or GBP. The skill checks eligibility. Mode is SINGLE. Currency changes on existing policies are unsupported.';
 if(field.csv_field==='PolicyViolationFlag')return 'Yes enables policy violation warnings under violation enforcement. Supply Warning Tolerance Percentage when Yes. Reimburse upper limit requires No.';
 if(field.csv_field==='WarningTolerance')return 'Enter a nonnegative percentage number when Policy Violation Warning is Yes. If Error Tolerance is also present, warning must be lower. Blank updates preserve stored values.';
 if(field.csv_field==='ErrorTolerance')return 'Enter a nonnegative percentage number when Prevent Report Submission is Yes. If Warning Tolerance is also present, error must be higher. Blank updates preserve stored values.';
 if(field.csv_field==='DispWarningToUserFlag')return 'Yes requires Policy Violation Warning Yes and violation enforcement. Reimburse upper limit requires No.';
 if(field.csv_field==='PreventSubmissionFlag')return 'Yes requires violation enforcement and Error Tolerance Percentage. Reimburse upper limit requires No.';
 if(field.csv_field==='PolicyEnforcementCode')return 'Choose Reimburse upper limit when expense exceeds defined rate or Generate policy violation when expense exceeds defined rate. The skill maps the label to its FSM code.';
 if(['EnabledRoleFlag','EnabledLocationFlag'].includes(field.csv_field))return 'Must be No when supplying reduced rate rows; child determinants are not available.';
 return field.boolean?'Enter Yes or No. Blank omits the value.':field.type==='date'?'Enter an Excel date or YYYY-MM-DD text.':field.type==='decimal'?'Enter a numeric amount without currency symbols.':'Enter the exact value. Blank omits the input.';
};
const guideRows=[];
for(const spec of catalog.sheets){
 const sheet=wb.worksheets.add(spec.name);base(sheet);const last=letter(spec.columns.length);const heading=letter(Math.min(spec.columns.length,6));title(sheet,spec.name,heading);
 sheet.getRange(`A2:${heading}2`).merge();sheet.getRange('A2').values=[[spec.kind==='rate'?
  (spec.entity==='ORA_EXM_MEALS_POLICY_LINE'?'Repeat Policy Name. Amounts use the parent currency and follow the parent limit flags.':'Repeat Policy Name. Enter the Daily Limit in the parent policy currency.'):
  'Enter one policy per row. Single currency (SINGLE) is fixed per policy. Enter Currency Code and choose the Policy Enforcement label.']];
 sheet.getRange(`A2:${heading}2`).format.wrapText=true;sheet.getRange(`A2:${heading}2`).format.rowHeight=38;
 sheet.getRange(`A4:${last}4`).values=[spec.columns.map(c=>c.label)];
 sheet.getRange(`A4:${last}4`).format={fill:'#D9D9D9',font:{bold:true},wrapText:true,rowHeight:50,verticalAlignment:'center'};
 sheet.getRange(`A5:${last}204`).format={fill:'#FFFFFF',rowHeight:24,
   borders:{preset:'all',style:'thin',color:'#B7B7B7'}};
 sheet.freezePanes.freezeRows(4);sheet.freezePanes.freezeColumns(1);
 spec.columns.forEach((field,i)=>{
  const col=letter(i+1);sheet.getRange(`${col}1:${col}204`).format.columnWidth=i===0?38:field.csv_field==='Description'?48:field.csv_field==='PolicyEnforcementCode'?76:25;
  const input=sheet.getRange(`${col}5:${col}204`);
  if(field.boolean)input.dataValidation={rule:{type:'list',values:field.fixed_value?[field.fixed_value]:['Yes','No']}};
  if(field.display_values)input.dataValidation={rule:{type:'list',values:Object.keys(field.display_values)}};
  if(field.fixed_value)input.values=Array.from({length:200},()=>[field.fixed_value]);
  if(field.type==='date')input.setNumberFormat('yyyy-mm-dd');
  else if(['decimal','double','number'].includes(field.type))input.setNumberFormat('#,##0.00');
  else input.setNumberFormat('@');
  guideRows.push([spec.name,field.label,notes(spec,field)]);
 });
}
const guide=wb.worksheets.add('Field Guide');base(guide);title(guide,'Field Guide','C');
guide.getRange('A4:C4').values=[['Sheet','Field','How to supply the value']];
guide.getRange('A4:C4').format={fill:'#D9D9D9',font:{bold:true},rowHeight:30};
guide.getRange(`A5:C${guideRows.length+4}`).values=guideRows;
guide.getRange(`A5:C${guideRows.length+4}`).format={rowHeight:42,wrapText:true,verticalAlignment:'center'};
guide.getRange('A1:A65').format.columnWidth=26;guide.getRange('B1:B65').format.columnWidth=35;guide.getRange('C1:C65').format.columnWidth=100;
guide.freezePanes.freezeRows(4);
wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
if(previews){await fs.mkdir(previews,{recursive:true});for(const name of ['Start Here',...catalog.sheets.map(s=>s.name),'Field Guide']){
 const image=await wb.render({sheetName:name,range:name==='Start Here'?'A1:B26':name==='Field Guide'?'A1:C20':`A1:${letter(Math.min(catalog.sheets.find(s=>s.name===name).columns.length,6))}8`,scale:1,format:'png'});
 await fs.writeFile(path.join(previews,name.replaceAll(' ','-')+'.png'),new Uint8Array(await image.arrayBuffer()));
}}
await(await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(JSON.stringify({output,sheets:catalog.sheets.length+2,inputSheets:catalog.sheets.length,inputFields:guideRows.length}));
