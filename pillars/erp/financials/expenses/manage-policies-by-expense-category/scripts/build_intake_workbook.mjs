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
// Limit font cells to the existing input footprint. Formatting unused columns
// materializes blank XML cells and slows every subsequent workbook preflight.
const base=(sheet,last)=>{sheet.showGridLines=true;sheet.getRange(`A1:${last}205`).format.font={name:'Arial',size:11};};
const title=(sheet,text,last)=>{
  sheet.getRange(`A1:${last}1`).merge();sheet.getRange('A1').values=[[text]];
  sheet.getRange(`A1:${last}1`).format={fill:'#595959',font:{name:'Arial',size:16,bold:true,color:'#FFFFFF'},rowHeight:32};
};
const start=wb.worksheets.add('Start Here');base(start,'B');title(start,'Manage Policies by Expense Category','B');
start.getRange('A1:A24').format.columnWidth=27;start.getRange('B1:B24').format.columnWidth=105;
const instructions=[
 ['Category','Meals, Accommodations, Entertainment, Airfare, Car Rental, Mileage, Miscellaneous and Per Diem policies and rates.'],
 ['Supported operations','All eight categories support their reviewed create/update profiles. Selected Airfare, Car Rental, Mileage, Miscellaneous and Per Diem creates passed live reconciliation. See references/live-verification-scope.md for the exact tested configurations. Other combinations and targets require their own validation and reconciliation. Exact unresolved update fields still require candidate-specific review.'],
 ['Lookup preflight','Dropdowns provide choices; they do not prove eligibility. Preflight must verify the selected lookup value and context against the target environment. Unresolved checks block candidate creation.'],
 ['Enter values','Use one row per policy and one row per rate. Multiple policies and rates are supported. Repeat the exact Policy Name on each associated rate.'],
 ['Blank cells','Blank updates preserve existing values, except fixed Daily Limit Yes and explicit upper-limit enforcement, which sets disabled warning/display/prevention controls to No and clears both tolerances.'],
 ['Rate currency','Use an enabled, active single currency where the selected monetary branch requires it. Airfare has no currency input; Miscellaneous Percentage reimbursement does not require a monetary rate currency. Preserve existing currency and mode on updates.'],
 ['Rate determinants','Role, location, seasonal rate and gender are not user inputs. Each selected policy must not require them. Existing sibling rates are validated; unrelated setup is preserved.'],
 ['Meals limits','Enable Single Instance Limit, Daily Sum Limit or both. Supply every enabled rate amount. Leave disabled amounts blank. Blank updates preserve saved values; disabling a populated limit is unsupported.'],
 ['Daily limits','Accommodations and Car Rental Daily Limit? shows one grey merged Yes for all policy rows. Blank row cells inherit Yes; preflight rejects No/N. Supply a Daily Limit on each rate.'],
 ['Policy Enforcement','Use the choices on the owning category sheet. Airfare flight-class enforcement and Miscellaneous reimbursement modes have their own choices and dependencies.'],
 ['Dates','Use Excel dates or YYYY-MM-DD. Supply End Date for bounded periods; blank means open-ended. Reuse exact existing Start/End Date and all other key coordinates for updates. Inclusive overlap checks follow the category and rate identity; distinct add-on/time components are separate rows.'],
 ['Category-specific inputs','Rate Determinants and Status are excluded. Use only fields provided on the applicable category sheet. Per Diem includes meal/accommodation controls; Miscellaneous includes Rate Type.'],
 ['Warning controls','Selecting Reimburse upper limit assumes warning/display/prevention No and empty tolerances. No confirmation is needed. Yes or any nonempty tolerance, even zero, is rejected. Under violation enforcement, enabled controls require their tolerances.'],
 ['Enforcement controls','For the original monetary-limit profiles, Reimburse upper limit requires warning, display and prevention controls No. Display Warning to User Yes requires Policy Violation Warning Yes. Airfare and Miscellaneous use their own enforcement rules. Blank updates preserve stored values.'],
 ['New records','Supply complete parent/rate groups and explicit active business choices. Status is managed: new parents and ordinary rates Draft; Per Diem ANCHOR rates Valid and other admitted rates Draft under its source recipe. No automatic closing, deleting or activation. Source qualification does not prove native create acceptance.'],
 ['Mileage and Miscellaneous creates','Mileage requires a base rate and all enabled passenger/company rates, exact threshold identities and target company references. Miscellaneous requires explicit rate mode, eligibility, limits and annual reset controls with every enabled amount. Blanks never invent a business default.'],
 ['Per Diem creates','For wholly new groups, choose the formula, includes, conversion and deductions explicitly; supply one ANCHOR and all active components/ranges with matching dates. Exact deduction value companions are internal task effects. New OTHER_STANDARD lower bounds, equal-hour minute ties and child/value creation for existing parents remain pending.'],
 ['Entertainment attendees','Capture Number of Attendees? Yes requires a threshold amount and currency, display controls No and rate limits No. Otherwise choose employee/nonemployee display, dependent field visibility and attendee requirements. Hidden, Optional and Required map to their stored codes.'],
 ['Entertainment rates','Enable Rate Limit? Yes requires Single Instance, Daily Sum or Yearly Limit, or a combination. Supply each enabled amount. Yearly Limit requires a Period Start Month and Day. February allows days 1–28. With no Rate Determinants, limits apply to the total receipt.'],
 ['Entertainment enforcement','Generate policy violation requires Policy Violation Warning or Prevent Report Submission Yes. New count-only or attendee-information-only policies may omit rates. Blank updates preserve values; switching modes cannot implicitly clear dependent settings.'],
];
for(let i=0;i<instructions.length;i++){
 const row=i*2+3;start.getRange(`A${row}:B${row}`).values=[instructions[i]];
 start.getRange(`A${row}`).format.font={bold:true};start.getRange(`B${row}`).format.wrapText=true;
 if(instructions[i][0]==='Mileage and Miscellaneous creates')start.getRange(`A${row}`).format.wrapText=true;
 start.getRange(`A${row}:B${row}`).format.rowHeight=42;
}
const notes=(sheet,field)=>{
 if(sheet.entity==='ORA_EXM_PERDIEM_POLICY_LINE'){
  if(field.csv_field==='BaseRate')return 'Daily rate: combined daily amount. Sum of separate rates: meals daily amount. Time ranges: monetary amount when Time Calculation Method is Rate. Percentage time ranges use separate value rows; new percentage time-range creation remains unqualified.';
  if(field.csv_field==='TypeOfLineCode')return 'Choose the component explicitly, including the ANCHOR head. Components and upper bounds distinguish rows sharing dates. New OTHER_STANDARD lower coordinates remain pending; compatible existing OTHER_STANDARD updates retain exact identity.';
  if(field.csv_field==='LineHours')return 'Time-range upper bound: 0–24 hours, or 999 for the upper-limit row. New ranges require distinct upper hours; equal-hour minute tie ordering is pending. This is a range threshold, not an eligibility clock hour.';
  if(field.csv_field==='LineMinutes')return 'Time-range upper-bound minutes: 0–60, following the captured setup page range.';
  if(field.csv_field?.endsWith('Deduction'))return 'Nonnegative deduction amount or percentage for the active calculation and deduction type. New groups generate only exact task-owned deduction companions. Existing dependent effects require exact candidate review; new value rows for existing parents and deletion remain unqualified.';
 }
 if(sheet.entity==='ORA_EXM_PERDIEM_POLICY'){
  if(field.csv_field?.includes('Elig') && /Hour$|Minute$/.test(field.csv_field))return 'Eligibility clock input. Captured UI allows hours 0–24 and minutes 0–60. Supply only for the applicable included component and deduction branch.';
  if(field.csv_field==='AccomMinNightHoursStay')return 'Minimum night stay: 0–24 hours when accommodation deduction/eligibility applies.';
 }
 if(field.workbook_only)return 'Always Yes for '+sheet.name+'. One grey merged Yes applies to every policy row, including blank row cells. Preflight rejects No/N. Display indicator only; no parent CSV flag is written.';
 const upperControl=['ORA_EXM_CARRENTAL_POLICY','ORA_EXM_MISCELLANEOUS_POLICY'].includes(sheet.entity)&&['PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag'].includes(field.csv_field);
 if(field.lookup&&!upperControl)return 'Select the provided choice or exact reference code as applicable. Target lookup eligibility and context are checked separately during preflight; unresolved evidence blocks import. Blank updates preserve saved values.';
 if(field.csv_field.endsWith('.PolicyName'))return 'Repeat the exact Policy Name from the parent sheet. This is an association, not an Oracle ID.';
 if(sheet.entity==='ORA_EXM_ENTERTAINMENT_POLICY'){
  if(['EmpAttendeeAmtCode','NonempAttendeeTypeCode','NonempAttendeeAmtCode','NonempJobTitleCode'].includes(field.csv_field))return 'Choose Hidden, Optional or Required when the corresponding attendee display is Yes. Leave blank when display is No. Blank updates preserve saved values.';
  if(field.csv_field==='PeriodMonth')return 'Required when Yearly Limit is Yes. Choose January through December. Leave blank when Yearly Limit is No.';
  if(field.csv_field==='PeriodDay')return 'Required when Yearly Limit is Yes. Enter a day within the selected month. February permits 1–28.';
  if(field.csv_field==='NumOfAttendeesFlag')return 'Yes captures the attendee count above a threshold and requires both attendee display controls and Enable Rate Limit to be No. No captures attendee information.';
  if(field.csv_field==='NumOfAttendeesAmount')return 'Required nonnegative threshold when Capture Number of Attendees? is Yes. Otherwise leave blank.';
  if(field.csv_field==='NumOfAttendeesCurrCode')return 'Required enabled, active threshold currency code when capturing attendee counts. Existing currency changes are outside the initial profile.';
  if(field.csv_field==='EnabledRateLimitFlag')return 'Choose Yes to define rate limits and enforcement. Choose No for a new policy without rate limits and leave rate definition, currency and enforcement fields blank.';
 }
 if(field.csv_field==='YearlyLimit')return 'Supply when Yearly Limit? is Yes. Otherwise leave blank. Amount uses the parent policy currency.';
 if(field.csv_field==='SingleInstanceLimit')return 'Supply when Single Instance Limit? is Yes. Otherwise leave blank. Amounts use the parent policy currency.';
 if(field.csv_field==='DailyLimit')return sheet.entity==='ORA_EXM_MEALS_POLICY_LINE'?'Supply when Daily Sum Limit? on Meals is Yes. Otherwise leave blank. Amounts use the parent policy currency.':'Daily monetary limit in the parent policy currency.';
 if(field.csv_field==='EndDate')return 'Optional inclusive end of this period. Leave blank only for an open-ended period. On updates supply the exact existing End Date key; key changes are unsupported. Periods must not overlap.';
 if(field.csv_field==='CurrencyCode')return 'Enter an enabled, active parent currency code where the selected monetary branch requires it. Miscellaneous Percentage reimbursement needs no monetary currency. Existing currency/mode changes are unsupported; blank input preserves the stored value.';
 if(field.csv_field==='PolicyViolationFlag')return 'Upper limit assumes No; leave blank or enter No. Yes cannot be set for an upper limit policy. Under violation enforcement, Yes requires Warning Tolerance Percentage.';
 if(field.csv_field==='WarningTolerance')return 'Upper limit requires empty; any supplied value, even zero, is rejected. Explicit upper-limit selection clears a saved tolerance. Under violation enforcement, enter a nonnegative percentage when warning is Yes; warning must be lower than error.';
 if(field.csv_field==='ErrorTolerance')return 'Upper limit requires empty; any supplied value, even zero, is rejected. Explicit upper-limit selection clears a saved tolerance. Under violation enforcement, enter a nonnegative percentage when prevention is Yes; error must exceed warning.';
 if(field.csv_field==='DispWarningToUserFlag')return 'Upper limit assumes No; leave blank or enter No. Yes cannot be set for an upper limit policy. Under violation enforcement, Yes requires Policy Violation Warning Yes.';
 if(field.csv_field==='PreventSubmissionFlag')return 'Upper limit assumes No; leave blank or enter No. Yes cannot be set for an upper limit policy. Under violation enforcement, Yes requires Error Tolerance Percentage.';
 if(field.csv_field==='PolicyEnforcementCode')return 'Choose Reimburse upper limit when expense exceeds defined rate or Generate policy violation when expense exceeds defined rate. The skill maps the label to its FSM code.';
 if(['EnabledRoleFlag','EnabledLocationFlag'].includes(field.csv_field))return 'Must be No when supplying reduced rate rows; child determinants are not available.';
 return field.boolean?'Enter Yes or No. Blank omits the value.':field.type==='date'?'Enter an Excel date or YYYY-MM-DD text.':field.type==='decimal'?'Enter a numeric amount without currency symbols.':'Enter the exact value. Blank omits the input.';
};
const createGuide=entity=>{
 if(['ORA_EXM_MILEAGE_POLICY','ORA_EXM_MILEAGE_LINE'].includes(entity))return 'Base MILEAGE creation without add-ons passed live reconciliation. Other groups require their own checks. Supply explicit controls and full identities; company references require target evidence. No Rate Determinants.';
 if(entity.startsWith('ORA_EXM_MISCELLANEOUS_POLICY'))return 'Complete new parent/rate groups or exact existing updates. Supply active rate mode, eligibility, limits and annual controls. No Rate Determinants; target checks and native approval remain required.';
 if(entity.startsWith('ORA_EXM_PERDIEM_POLICY'))return 'Wholly new formula-specific groups or exact existing updates. Explicit ANCHOR and matching dates required. Internal deduction values are task-owned. New OTHER_STANDARD lower bounds/equal-hour ties and child creation for existing parents remain pending.';
 return null;
};
const guideRows=[];
for(const spec of catalog.sheets){
 const sheet=wb.worksheets.add(spec.name);base(sheet,letter(Math.min(spec.columns.length,27)));const last=letter(spec.columns.length);const heading=letter(Math.min(spec.columns.length,6));title(sheet,spec.name,heading);
 sheet.getRange(`A2:${heading}2`).merge();sheet.getRange('A2').values=[[['ORA_EXM_CARRENTAL_POLICY','ORA_EXM_CARRENTAL_POLICY_LINE'].includes(spec.entity) ? 'Selected SINGLE USD100 daily-limit creation passed live reconciliation. Include a parent and rates with explicit choices. Other cases need their own checks. No Rate Determinants; existing updates retain key and field-review gates.' : ['ORA_EXM_AIRFARE_POLICY','ORA_EXM_AIRFARE_POLICY_LINE'].includes(spec.entity) ? 'Selected no-determinant CATCH_ALL/COACH creation passed live reconciliation. Supply enforcement/display choices, Flight Class and Start Date. Other cases need their own checks. No currency inputs; updates retain key and field-review gates.' : createGuide(spec.entity) ? createGuide(spec.entity) : spec.kind==='rate'?
  (spec.entity==='ORA_EXM_ACCOM_POLICY_LINE'?'Repeat Policy Name. Enter the Daily Limit in the parent policy currency.':'Repeat Policy Name. Supply amounts for each enabled parent limit. Amounts use the parent currency.'):
  (spec.entity==='ORA_EXM_ENTERTAINMENT_POLICY'?'Choose attendee capture mode and dependent controls. Rate limits are optional. Annual limits require a reset month and day.':'Enter one policy per row. Single currency (SINGLE) is fixed per policy. Enter Currency Code and choose the Policy Enforcement label.')]];
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
  if(field.fixed_value){input.merge();sheet.getRange(`${col}5`).values=[[field.fixed_value]];input.format.fill='#D9D9D9';input.format.font={color:'#595959'};input.format.verticalAlignment='top';input.format.borders={preset:'outside',style:'thin',color:'#B7B7B7'};}
  if(field.type==='date')input.setNumberFormat('yyyy-mm-dd');
  else if(['int','integer','long','short'].includes(field.type))input.setNumberFormat('0');
  else if(['decimal','double','number'].includes(field.type))input.setNumberFormat('#,##0.00');
  else input.setNumberFormat('@');
  guideRows.push([spec.name,field.label,notes(spec,field)]);
 });
}
const guide=wb.worksheets.add('Field Guide');base(guide,'C');title(guide,'Field Guide','C');
guide.getRange('A4:C4').values=[['Sheet','Field','How to supply the value']];
guide.getRange('A4:C4').format={fill:'#D9D9D9',font:{bold:true},rowHeight:30};
guide.getRange(`A5:C${guideRows.length+4}`).values=guideRows;
guide.getRange(`A5:C${guideRows.length+4}`).format={rowHeight:42,wrapText:true,verticalAlignment:'center'};
guide.getRange('A1:A65').format.columnWidth=26;guide.getRange('B1:B65').format.columnWidth=35;guide.getRange('C1:C65').format.columnWidth=100;
guide.freezePanes.freezeRows(4);
wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
if(previews){await fs.mkdir(previews,{recursive:true});for(const name of ['Start Here',...catalog.sheets.map(s=>s.name),'Field Guide']){
 const image=await wb.render({sheetName:name,range:name==='Start Here'?'A1:B28':name==='Field Guide'?'A1:C20':`A1:${letter(Math.min(catalog.sheets.find(s=>s.name===name).columns.length,6))}8`,scale:1,format:'png'});
 await fs.writeFile(path.join(previews,name.replaceAll(' ','-')+'.png'),new Uint8Array(await image.arrayBuffer()));
 if(name==='Entertainment')for(const [label,range] of [['attendees','F4:N8'],['limits','O4:U8'],['enforcement','V4:AA8']]){
  const detail=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(previews,`Entertainment-${label}.png`),new Uint8Array(await detail.arrayBuffer()));
 }
}}
await(await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(JSON.stringify({output,sheets:catalog.sheets.length+2,inputSheets:catalog.sheets.length,inputFields:guideRows.length}));
