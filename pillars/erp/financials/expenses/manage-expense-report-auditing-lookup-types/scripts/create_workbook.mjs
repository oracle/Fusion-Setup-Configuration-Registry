#!/usr/bin/env node
// Author with the installed spreadsheet skill's bundled Node and artifact-tool.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile, FileBlob} from '@oai/artifact-tool';
try {
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = {};
for (let i=2;i<process.argv.length;i++) {
  const flag=process.argv[i];
  if (['--help','--dry-run','--offline-starter'].includes(flag)) args[flag.slice(2)]=true;
  else if (['--output','--catalog','--input','--preview','--lov-catalog','--environment'].includes(flag) && process.argv[i+1]) args[flag.slice(2)]=process.argv[++i];
  else throw new Error('Unknown or incomplete argument: '+flag);
}
if (args.help || !args.output) {
  console.log('create_workbook.mjs --output FILE.xlsx --lov-catalog verified-lovs.json --environment NAME [--input corrected-model.json] [--preview PREFIX] [--dry-run]\nUse --offline-starter instead of --lov-catalog only for an unverified portable template.');
  process.exit(0);
}
const catalog=JSON.parse(await fs.readFile(args.catalog ?? path.join(root,'references/intake-fields.json'),'utf8'));
if (!args['lov-catalog'] && !args['offline-starter']) throw new Error('Refresh customer references and pass --lov-catalog. Use --offline-starter only for a portable unverified authoring template.');
const lovs=JSON.parse(await fs.readFile(args['lov-catalog'] ?? path.join(root,'references/workbook-lovs.json'),'utf8'));
if (args['lov-catalog']) {
 const age=Date.now()-Date.parse(lovs.captured_at);
 if (lovs.catalog_kind!=='customer-environment' || !args.environment || lovs.environment!==args.environment || !Number.isFinite(age) || age < -60000 || age > 3600000) throw new Error('Customer dropdowns need a fresh catalog from the explicitly selected environment.');
}
const literal=v=>typeof v==='string'&&v.startsWith('=')?"'"+v:v;
const model=args.input ? JSON.parse(await fs.readFile(args.input,'utf8')) : {rows:[]};
if (lovs.task_code!=='EXM_MANAGE_AUDIT_LOOKUP_TYPES' || !Array.isArray(model.rows) || !Array.isArray(lovs.lookup_types) || !Array.isArray(lovs.reference_sets)) throw new Error('Task or input catalog mismatch.');
for (const list of [lovs.lookup_types,lovs.reference_sets]) {
  if ((!list.length && !args['offline-starter']) || list.length>10000 || new Set(list.map(x=>x.code)).size!==list.length || list.some(x=>typeof x.code!=='string' || (!x.code || x.code.length>30 || /[\x00-\x1F]/.test(x.code)))) throw new Error('Provide unique, literal verified LOV codes.');
}
if (!Array.isArray(model.type_rows??[]) || model.source_issues?.length || model.issues?.length || model.rows.some(row=>Object.keys(row).some(key=>!catalog.fields.some(f=>f.key===key))) || (model.type_rows??[]).some(row=>Object.keys(row).some(key=>!catalog.type_sheet.fields.some(f=>f.key===key)))) throw new Error('Resolve input issues and revalidate the complete model before generation.');
if (args['dry-run']) { console.log(JSON.stringify({status:'valid',rows:model.rows.length,typeRows:(model.type_rows??[]).length,lookupTypes:lovs.lookup_types.length,referenceSets:lovs.reference_sets.length,outputWritten:false})); process.exit(0); }
try { await fs.access(args.output); throw new Error('Refusing to overwrite output.'); }
catch (e) { if (e.code!=='ENOENT') throw e; }
const wb=Workbook.create(), sh=wb.worksheets.add(catalog.sheet_name), types=wb.worksheets.add('Lookup Types'), refs=wb.worksheets.add('Reference Lists');
const first=catalog.first_data_row,last=Math.max(200,model.rows.length)+first-1,header=catalog.header_row;
for (const s of [sh,refs]) { s.showGridLines=false; s.tabColor=s===sh?'#595959':'#595959'; }
sh.getRange(`A1:J${last}`).format.font={name:'Arial',size:11,color:'#000000'};
sh.getRange(`A1:J${last}`).format.verticalAlignment='center';
sh.getRange('A1').values=[['Manage Expense Report Auditing Lookup Types']];
sh.getRange('A1').format.font={name:'Arial',size:16,bold:true,color:'#000000'};
sh.getRange('A1:J1').format.rowHeight=32;
const instructions=[
 'For updates, leave a cell blank to keep its current value.',
 '',
 '',
 '', '', ''
];
sh.getRange('A2:A7').values=instructions.map(x=>[x]);
sh.getRange('A2:J2').format.rowHeight=24;
sh.getRange('A3:J7').format.rowHeight=8;
sh.getRange('A6').format.font={name:'Arial',size:11,italic:true,color:'#4A6556'};
const headers=catalog.fields.map(f=>f.label+(['always','create'].includes(f.required_for)?' *':''));
sh.getRange(`A${header}:J${header}`).values=[headers];
sh.getRange(`A${header}:J${header}`).format={fill:'#D9D9D9',font:{name:'Arial',size:11,bold:true,color:'#000000'},wrapText:true,rowHeight:50,horizontalAlignment:'left'};
sh.getRange(`A${first}:J${last}`).format.fill='#FFFFFF';
sh.getRange(`A${first}:J${last}`).format.rowHeight=24;
sh.getRange(`A${first}:J${last}`).setNumberFormat('@');
const widths=[32,38,25,44,65,13,17,17,19,24];
widths.forEach((w,i)=>sh.getRangeByIndexes(0,i,last,1).format.columnWidth=w);
// Stack the two reference tables so customers do not need horizontal scrolling.
const setHeader=Math.max(1,lovs.lookup_types.length)+8;
const refLast=setHeader+Math.max(1,lovs.reference_sets.length);
refs.getRange(`A1:C${refLast}`).format.font={name:'Arial',size:11,color:'#000000'};
refs.getRange(`A1:C${refLast}`).format.verticalAlignment='center';
refs.getRange('A1').values=[['Manage Expense Report Auditing Lookup Types']];
refs.getRange('A1:C1').format.rowHeight=32;
refs.getRange('A2').values=[['Available Lookup Types and Reference Data Sets']];
refs.getRange('A3').values=[[args['offline-starter'] ? '' : `Environment: ${args.environment}   Refreshed: ${lovs.captured_at}`]];
refs.getRange('A2:C3').format.rowHeight=30;
refs.getRange('A4:C4').values=[['Lookup Type','Meaning','Configuration Level']];
const names={S:'System',E:'Extension',U:'User'};
if(lovs.lookup_types.length) refs.getRangeByIndexes(4,0,lovs.lookup_types.length,3).values=lovs.lookup_types.map(x=>[x.code,x.name??x.code,names[x.configuration_level]??'Not available'].map(literal));
refs.getRange(`A${setHeader-1}:C${setHeader-1}`).merge();
refs.getRange(`A${setHeader-1}`).values=[['Reference Data Sets']];
refs.getRange(`A${setHeader-1}:C${setHeader-1}`).format={font:{name:'Arial',size:12,bold:true},rowHeight:28};
refs.getRange(`A${setHeader}:B${setHeader}`).values=[['Reference Data Set Code','Set Name']];
if(lovs.reference_sets.length) refs.getRangeByIndexes(setHeader,0,lovs.reference_sets.length,2).values=lovs.reference_sets.map(x=>[x.code,x.name??x.code].map(literal));
[34,44,30].forEach((w,i)=>refs.getRangeByIndexes(0,i,refLast,1).format.columnWidth=w);
refs.getRange(`A5:C${refLast}`).format.wrapText=true;
refs.getRange(`A5:C${refLast}`).format.rowHeight=40;
for(const area of ['A4:C4',`A${setHeader}:B${setHeader}`]) refs.getRange(area).format={fill:'#D9D9D9',font:{name:'Arial',size:11,bold:true,color:'#000000'},wrapText:true,rowHeight:40,horizontalAlignment:'left'};
refs.tables.add(`A4:C${Math.max(1,lovs.lookup_types.length)+4}`,true,'AuditingLookupTypes');
refs.tables.add(`A${setHeader}:B${refLast}`,true,'AuditingReferenceSets');
refs.freezePanes.freezeRows(4);
// INDIRECT is an Excel list-source formula; it creates no executable worksheet cells.
for (const [column,tableName,fieldName] of [['A','AuditingLookupTypes','Lookup Type'],['C','AuditingReferenceSets','Reference Data Set Code']]) {
 sh.getRange(`${column}${first}:${column}${last}`).dataValidation={rule:{type:'list',formula1:`INDIRECT("${tableName}[${fieldName}]")`},errorAlert:{style:'warning',title:'Verify an existing value',message:'Choose a value from the list. If it is missing, refresh the list from your environment.'}};
}
sh.getRange(`F${first}:F${last}`).dataValidation={rule:{type:'list',values:['Yes','No']},errorAlert:{style:'stop',title:'Choose Yes or No',message:'Select Yes or No.'}};
sh.getRange(`G${first}:H${last}`).setNumberFormat('yyyy-mm-dd');
sh.getRange(`G${first}:H${last}`).dataValidation={rule:{type:'date',operator:'between',formula1:'=DATE(1900,1,1)',formula2:'=DATE(9999,12,31)'},prompt:{title:'Date format',message:'YYYY-MM-DD, for example 2026-11-03.'},errorAlert:{style:'stop',title:'Enter a valid date',message:'Enter a valid date, for example 2026-11-03, or leave blank.'}};
sh.getRange(`I${first}:I${last}`).setNumberFormat('0');
for (const [index,record] of model.rows.entries()) {
 const values=catalog.fields.map(f=>{const v=record[f.key]??null;if(f.kind==='date'&&typeof v==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(v))return new Date(v+'T00:00:00Z');return typeof v==='string'&&v.startsWith('=')?"'"+v:v;});
 sh.getRangeByIndexes(first-1+index,0,1,10).values=[values];
 sh.getRangeByIndexes(first-1+index,0,1,10).format.rowHeight=60;
}
sh.getRange(`B${first}:E${last}`).format.wrapText=true;
sh.tables.add(`A${header}:J${last}`,true,'AuditingLookupCodes');
sh.freezePanes.freezeRows(header); sh.freezePanes.freezeColumns(2);
const typeLast=Math.max(200,(model.type_rows??[]).length)+first-1;
types.showGridLines=false; types.tabColor='#595959';
types.getRange(`A1:C${typeLast}`).format.font={name:'Arial',size:11,color:'#000000'};
types.getRange(`A1:C${typeLast}`).format.verticalAlignment='center';
types.getRange('A1').values=[['Manage Expense Report Auditing Lookup Types']];
types.getRange('A1').format.font={name:'Arial',size:16,bold:true,color:'#000000'};
types.getRange('A1:C1').format.rowHeight=32;
types.getRange('A2:A7').values=[
 ['Update an existing Lookup Type: enter Meaning, Description, or both.'],
 ['Leave Meaning or Description blank to keep its current value.'],
 [''],
 ['',], ['',], ['',]
];
types.getRange('A2:C3').format.rowHeight=24;
types.getRange('A4:C7').format.rowHeight=8;
types.getRange(`A${header}:C${header}`).values=[['Lookup Type *','Meaning','Description']];
types.getRange(`A${header}:C${header}`).format={fill:'#D9D9D9',font:{name:'Arial',size:11,bold:true,color:'#000000'},wrapText:true,rowHeight:50,horizontalAlignment:'left'};
types.getRange(`A${first}:C${typeLast}`).format.fill='#FFFFFF';
types.getRange(`A${first}:C${typeLast}`).format.rowHeight=24;
types.getRange(`A${first}:C${typeLast}`).setNumberFormat('@');
[34,48,78].forEach((w,i)=>types.getRangeByIndexes(0,i,typeLast,1).format.columnWidth=w);
types.getRange(`A${first}:A${typeLast}`).dataValidation={rule:{type:'list',formula1:'INDIRECT("AuditingLookupTypes[Lookup Type]")'},errorAlert:{style:'warning',title:'Verify an existing type',message:'Choose a Lookup Type from the list. If it is missing, refresh the list from your environment.'}};
for (const [index,record] of (model.type_rows??[]).entries()) {
 types.getRangeByIndexes(first-1+index,0,1,3).values=[catalog.type_sheet.fields.map(f=>{const v=record[f.key]??null;return typeof v==='string'&&v.startsWith('=')?"'"+v:v;})];
 types.getRangeByIndexes(first-1+index,0,1,3).format.rowHeight=60;
}
types.getRange(`B${first}:C${typeLast}`).format.wrapText=true;
types.tables.add(`A${header}:C${typeLast}`,true,'AuditingTypeChanges');
types.freezePanes.freezeRows(header);types.freezePanes.freezeColumns(1);
for (const [sheet,end,start,lastRow] of [[sh,'J',first,last],[types,'C',first,typeLast]]) {
 sheet.getRange(`A1:${end}1`).format.fill='#595959'; sheet.getRange(`A1:${end}1`).format.font={name:'Arial',size:16,bold:true,color:'#FFFFFF'};
 sheet.getRange(`A${start}:${end}${lastRow}`).format.borders={preset:'all',style:'thin',color:'#B7B7B7'};
 for (const table of sheet.tables.items) table.style='TableStyleLight1';
}
refs.getRange('A1:C1').format.fill='#595959';refs.getRange('A1:C1').format.font={name:'Arial',size:16,bold:true,color:'#FFFFFF'};
for (const table of refs.tables.items) table.style='TableStyleLight1';
for (const [sheet,end] of [[sh,'J'],[types,'C'],[refs,'C']]) {
 sheet.getRange(`A1:${end}1`).merge();
 const endRow=sheet===refs?3:7;
 for(let row=2;row<=endRow;row++) {sheet.getRange(`A${row}:${end}${row}`).merge();sheet.getRange(`A${row}:${end}${row}`).format.wrapText=true;}
}
// Field guidance and limits use the same catalog as workbook intake.
for (const [sheet,fields,columns,endRow] of [
 [sh,catalog.fields,['B','D','E','J'],last],
 [types,catalog.type_sheet.fields,['B','C'],typeLast]
]) {
 for (const column of columns) {
  const index=column.charCodeAt(0)-65, field=fields[index];
  sheet.getRange(`${column}${first}:${column}${endRow}`).dataValidation={
   rule:{type:'textLength',operator:'lessThanOrEqual',formula1:field.maximum},
   errorAlert:{style:'stop',title:'Text is too long',message:`${field.label}: enter no more than ${field.maximum} characters.`}
  };
 }
}
sh.getRange(`I${first}:I${last}`).dataValidation={
 rule:{type:'custom',formula1:`=OR(I${first}="",IFERROR(AND(ISNUMBER(I${first}),I${first}=INT(I${first}),ABS(I${first})<10^18),FALSE))`},
 errorAlert:{style:'stop',title:'Enter a whole number',message:'Enter a whole number with at most 18 digits, or leave blank.'}
};
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:`Lookup Codes!A${header}:J${first+1}`,include:'values,formulas',tableMaxRows:3,tableMaxCols:10,maxChars:1600})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
await fs.mkdir(path.dirname(args.output),{recursive:true});
await (await SpreadsheetFile.exportXlsx(wb)).save(args.output);
if(args.preview) {
 const saved=await SpreadsheetFile.importXlsx(await FileBlob.load(args.output));
 for(const [suffix,sheetName,range] of [['input','Lookup Codes','A1:J12'],['types','Lookup Types','A1:C12'],['references','Reference Lists','A1:C12'],['sets','Reference Lists',`A${setHeader-1}:C${Math.min(refLast,setHeader+4)}`]]) {
  const preview=await saved.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`${args.preview}-${suffix}.png`,new Uint8Array(await preview.arrayBuffer()));
 }
}

} catch (error) { console.error('Workbook generation failed: '+error.message); process.exitCode=1; }
