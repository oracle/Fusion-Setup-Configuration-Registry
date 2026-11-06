import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";

const skillDir = path.resolve(import.meta.dirname, "..");
const catalog = JSON.parse(await fs.readFile(path.join(skillDir, "references/intake-fields.json"), "utf8"));
const ROWS = 500;
const INHERIT = catalog.inherit_all;

function column(index) {
  let result = "";
  for (let n = index + 1; n; n = Math.floor((n - 1) / 26)) result = String.fromCharCode(65 + (n - 1) % 26) + result;
  return result;
}

function allowedValues(field) {
  const values = field.kind === "yes_no" ? ["Yes", "No"] : field.kind === "enum" ? field.choices.map(choice => choice.label) : [];
  if (field.key === "employee_liability_account") values.push(catalog.inherit_payables);
  values.push(INHERIT);
  return values;
}

function createSection(workbook, section, index) {
  const sheet = workbook.worksheets.add(section.sheet);
  const fields = section.fields;
  const last = column(fields.length);
  const end = ROWS + 4;
  const headings = ["Business Unit", ...fields.map(field => field.header)];
  sheet.showGridLines = false;
  sheet.mergeCells(`A1:${last}1`);
  sheet.mergeCells(`A2:${last}2`);
  sheet.mergeCells(`A3:${last}3`);
  sheet.getRange("A1").values = [[`Manage Expenses System Options — ${section.sheet}`]];
  sheet.getRange("A2").values = [["Enter one row per business unit. A fresh FSM setup-data export determines the operation: an existing business unit is Edit; an absent business unit is Create. For Edit, blank fields are unchanged and filled fields are changes. For Create, filled fields are setup values and blank fields are unset. See Field Guide."]];
  sheet.getRange("A3").values = [[`Use "${INHERIT}" to request inheritance on a specific business unit. Some displayed choices still require an exact FSM value-code check; the validator reports those as pending.`]];
  sheet.getRange(`A4:${last}4`).values = [headings];
  sheet.getRange("A5").values = [[catalog.global_business_unit]];
  sheet.getRange(`A1:${last}1`).format = {fill:"#595959",font:{name:"Arial",size:11,bold:true,color:"#FFFFFF"},verticalAlignment:"center"};
  sheet.getRange(`A2:${last}2`).format = {font:{name:"Arial",size:11},wrapText:true,verticalAlignment:"center"};
  sheet.getRange(`A3:${last}3`).format = {font:{name:"Arial",size:11,italic:true},wrapText:true,verticalAlignment:"center"};
  sheet.getRange(`A4:${last}4`).format = {fill:"#D0D0D0",font:{name:"Arial",size:11,bold:true,color:"#000000"},wrapText:true,verticalAlignment:"center"};
  sheet.getRange(`A5:${last}${end}`).format = {font:{name:"Arial",size:11},verticalAlignment:"center"};
  sheet.getRange("A1").format.rowHeight = 27;
  sheet.getRange("A2").format.rowHeight = 86;
  sheet.getRange("A3").format.rowHeight = 42;
  sheet.getRange("A4").format.rowHeight = 82;
  sheet.getRange(`A5:${last}${end}`).format.rowHeight = 26;
  sheet.getRange("A:A").format.columnWidth = 34;
  for (let i = 1; i <= fields.length; i++) {
    const col = column(i);
    sheet.getRange(`${col}:${col}`).format.columnWidth = Math.min(53, Math.max(25, fields[i - 1].header.length + 5));
    const values = allowedValues(fields[i - 1]);
    if (["yes_no", "enum"].includes(fields[i - 1].kind) || fields[i - 1].key === "employee_liability_account") {
      sheet.getRange(`${col}5:${col}${end}`).dataValidation = {rule:{type:"list",values}};
    }
  }
  const table = sheet.tables.add(`A4:${last}${end}`, true, `ExpensesOptions${index + 1}`);
  table.style = "TableStyleLight1";
  sheet.freezePanes.freezeRows(4);
}

function createGuide(workbook) {
  const sheet = workbook.worksheets.add("Field Guide");
  const headers = ["Section", "Field", "Scope", "Input type", "Available values / input", "FSM file", "Field code", "Mapping status"];
  const lines = catalog.sections.flatMap(section => section.fields.map(field => [
    section.sheet, field.header, field.scope ?? "All and specific", field.kind.replaceAll("_", " "),
    field.kind === "yes_no" ? "Yes; No" : field.kind === "enum" ? field.choices.map(x => x.label).join("; ") : "Enter a value; see skill guidance",
    field.source ?? "Unmapped", field.code ?? "Unmapped",
    field.kind === "enum" && field.choices.some(choice => !choice.code) ? `${field.mapping}; value codes incomplete` : field.mapping,
  ]));
  sheet.showGridLines = false;
  sheet.mergeCells("A1:H1");
  sheet.mergeCells("A2:H2");
  sheet.mergeCells("A3:H3");
  sheet.getRange("A1").values = [["Manage Expenses System Options — Field Guide"]];
  sheet.getRange("A2").values = [["Field names follow the supplied Oracle Fusion screens. Confirm FSM file and code mappings against a fresh target export. A candidate or unmapped field, or a choice without a confirmed code, requires review before an import can be prepared."]];
  sheet.getRange("A3").values = [[`The operation is resolved from the target's fresh setup-data export. Existing-business-unit blanks are unchanged; every filled field expresses change intent, even if it equals the exported value. "${INHERIT}" requests the all-business-units setting on a specific business unit. This is not an FSM import ZIP.`]];
  sheet.getRange("A4:H4").values = [headers];
  sheet.getRange(`A5:H${lines.length + 4}`).values = lines;
  sheet.getRange("A1:H1").format = {fill:"#595959",font:{name:"Arial",size:11,bold:true,color:"#FFFFFF"},verticalAlignment:"center"};
  sheet.getRange("A2:H2").format = {font:{name:"Arial",size:11},wrapText:true,verticalAlignment:"center"};
  sheet.getRange("A3:H3").format = {font:{name:"Arial",size:11,italic:true},wrapText:true,verticalAlignment:"center"};
  sheet.getRange("A4:H4").format = {fill:"#D0D0D0",font:{name:"Arial",size:11,bold:true,color:"#000000"},wrapText:true,verticalAlignment:"center"};
  sheet.getRange(`A5:H${lines.length + 4}`).format = {font:{name:"Arial",size:11},verticalAlignment:"center"};
  sheet.getRange("A1").format.rowHeight = 27;
  sheet.getRange("A2").format.rowHeight = 86;
  sheet.getRange("A3").format.rowHeight = 42;
  sheet.getRange("A4").format.rowHeight = 82;
  sheet.getRange(`A5:G${lines.length + 4}`).format.rowHeight = 26;
  [25, 53, 22, 23, 80, 26, 37, 22].forEach((width, i) => sheet.getRange(`${column(i)}:${column(i)}`).format.columnWidth = width);
  const table = sheet.tables.add(`A4:H${lines.length + 4}`, true, "ExpensesOptionsFieldGuide");
  table.style = "TableStyleLight1";
  sheet.freezePanes.freezeRows(4);
}

async function create(output) {
  const { SpreadsheetFile, Workbook } = await import("@oai/artifact-tool");
  const workbook = Workbook.create();
  catalog.sections.forEach((section, index) => createSection(workbook, section, index));
  createGuide(workbook);
  workbook.recalculate();
  await fs.mkdir(path.dirname(output), {recursive:true});
  await (await SpreadsheetFile.exportXlsx(workbook)).save(output);
  for (const section of catalog.sections) {
    const last = column(section.fields.length);
    const image = await workbook.render({sheetName:section.sheet,range:`A1:${last}9`,scale:1,format:"png"});
    await fs.writeFile(`${output}.${section.sheet.replaceAll(" ", "-")}.png`,new Uint8Array(await image.arrayBuffer()));
  }
  const image = await workbook.render({sheetName:"Field Guide",range:"A1:H10",scale:1,format:"png"});
  await fs.writeFile(`${output}.Field-Guide.png`,new Uint8Array(await image.arrayBuffer()));
  console.log(JSON.stringify({output,sheets:catalog.workbook_sheets,rows_per_input_sheet:ROWS}));
}

function issue(list, section, cell, message) { list.push({sheet:section,cell,message}); }

function csvRows(text) {
  const rows = [], row = [];
  let cell = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"') quoted = true;
    else if (char === ',') { row.push(cell); cell = ""; }
    else if (char === '\n' || char === '\r') {
      if (char === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); rows.push([...row]); row.length = 0; cell = "";
    } else cell += char;
  }
  if (quoted) throw new Error("Malformed baseline CSV: unclosed quoted field");
  if (cell || row.length) { row.push(cell); rows.push([...row]); }
  return rows;
}

function xmlValue(xml, name) {
  return xml.match(new RegExp(`<${name}>([^<]*)</${name}>`))?.[1] ?? null;
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function normalizedBusinessUnit(value) {
  return (value || catalog.global_business_unit).trim().toLocaleLowerCase("en-US");
}

function sameEnvironment(left, right) {
  return typeof left === "string" && typeof right === "string"
    && left.length > 0 && right.length > 0 && left.toLowerCase() === right.toLowerCase();
}

function confirmedOptionEdit(change) {
  const field = catalog.sections.flatMap(section => section.fields).find(field => field.key === change?.key);
  if (field?.mapping !== "confirmed" || field.source !== "EXM_SETUP_OPTION"
      || change.source !== field.source || change.code !== field.code || change.mode) return false;
  if (field.kind === "yes_no") return ["Yes", "No"].includes(change.value)
    && change.valueCode === (change.value === "Yes" ? "Y" : "N");
  return field.kind === "enum" && field.choices.some(choice => choice.code
    && choice.label === change.value && choice.code === change.valueCode);
}

function confirmedScalarSetting(change) {
  const field = catalog.sections.flatMap(section => section.fields).find(field => field.key === change?.key);
  return field?.mapping === "confirmed" && field.source === "EXM_ORG_SETTING"
    && ["text", "email", "nonnegative_integer"].includes(field.kind)
    && change.source === field.source && change.code === field.code && !change.mode
    && change.value !== null && change.value !== undefined && String(change.value).trim() !== "";
}

function confirmedChange(change) {
  return confirmedOptionEdit(change) || confirmedScalarSetting(change);
}

function importReadiness(records, issues, pendingChecks, baseline) {
  const import_blockers = [];
  if (!baseline) import_blockers.push("A fresh completed target data export is required.");
  if (!records.length) import_blockers.push("At least one requested option edit is required.");
  if (issues.length) import_blockers.push("Resolve all intake validation issues.");
  if (pendingChecks.length) import_blockers.push("Resolve all pending field-mapping or inheritance checks.");
  for (const record of records) {
    if (!["edit", "create"].includes(record.operation)) {
      import_blockers.push(`${record.sheet} row ${record.row}: resolve the target operation before FSM package preparation.`);
    }
    for (const change of record.changes) {
      if (!confirmedChange(change)) {
        import_blockers.push(`${record.sheet} row ${record.row}, ${change.label}: require a confirmed option code/value pair or supported scalar setting.`);
      }
    }
  }
  return {ready_for_import: import_blockers.length === 0, import_blockers};
}

function verifyBaselineArchive(directory, environment, processId, archivePath) {
  const expectedName = `${environment}_setup_task_csv_export_${catalog.source_export.task_code.toLowerCase()}_${processId}.zip`;
  const suffix = `_setup_task_csv_export_${catalog.source_export.task_code.toLowerCase()}_${processId}.zip`;
  const archiveName = path.basename(archivePath);
  if (!archiveName.endsWith(suffix) || !sameEnvironment(archiveName.slice(0, -suffix.length), environment)) {
    throw new Error(`Baseline archive name must be ${expectedName}`);
  }
  const helper = path.join(skillDir, "scripts/verify_baseline_archive.py");
  let result;
  try {
    result = execFileSync(process.env.PYTHON || "python3", [helper, archivePath, directory], {encoding:"utf8"});
  } catch (error) {
    throw new Error(`Baseline archive does not match extracted export: ${error.stderr?.toString().trim() || error.message}`);
  }
  return JSON.parse(result);
}

async function loadBaseline(directory, expectedEnvironment, processId, archivePath) {
  if (!/^\d+$/.test(processId ?? "")) throw new Error("--baseline-process-id must be the approved data-export ProcessId");
  const metadataPath = path.join(directory, "ASM_SETUP_CSV_METADATA.xml");
  const metadata = await fs.readFile(metadataPath, "utf8");
  if (xmlValue(metadata, "ObjectShortName") !== catalog.source_export.task_code || xmlValue(metadata, "ProcessStatus") !== "COMPLETED" || xmlValue(metadata, "ProcessType") !== "EXPORT") {
    throw new Error("Baseline metadata does not identify a completed export for this setup task");
  }
  const environment = xmlValue(metadata, "ProcessEnv");
  if (!environment || (expectedEnvironment && !sameEnvironment(environment, expectedEnvironment))) throw new Error("Baseline environment does not match the requested target");
  const metadataProcessId = xmlValue(metadata, "ProcessId");
  if (metadataProcessId !== processId && metadataProcessId !== "-999") {
    throw new Error("Baseline metadata ProcessId does not match --baseline-process-id");
  }
  if (metadataProcessId === "-999" && !archivePath) {
    throw new Error("Baseline metadata uses ProcessId -999; --baseline-archive is required to bind the extracted files to the export process");
  }
  const archive = archivePath ? verifyBaselineArchive(directory, environment, processId, archivePath) : null;
  const names = new Map(), hashes = {};
  let dataRows = 0;
  for (const filename of ["EXM_SETUP_OPTION.csv", "EXM_ORG_SETTING.csv", "EXM_CASH_ADV_SETUP_AND_POLICY.csv"]) {
    const bytes = await fs.readFile(path.join(directory, filename));
    hashes[filename] = createHash("sha256").update(bytes).digest("hex");
    const rows = csvRows(bytes.toString("utf8").replace(/^\uFEFF/, ""));
    const nameIndex = rows[0]?.indexOf("BuName") ?? -1;
    if (nameIndex < 0) throw new Error(`${filename} has no BuName column`);
    for (const row of rows.slice(1)) {
      if (!row.some(Boolean)) continue;
      dataRows++;
      // FSM leaves BuName empty for the All Business Units setup rows.
      const name = row[nameIndex]?.trim() || catalog.global_business_unit;
      const key = name.toLocaleLowerCase("en-US");
      if (names.has(key) && names.get(key) !== name) throw new Error(`Ambiguous business-unit capitalization in ${filename}`);
      names.set(key, name);
    }
  }
  // A completed data export may legitimately contain no configured values.
  // Its EXPORT metadata and process binding distinguish it from a template.
  return {directory,process_id:processId,metadata_process_id:metadataProcessId,environment,process_date:xmlValue(metadata,"ProcessDate"),archive_sha256:archive?.archive_sha256 ?? null,file_sha256:hashes,business_units:names};
}

async function validate(input, output, baseline) {
  const { FileBlob, SpreadsheetFile } = await import("@oai/artifact-tool");
  const inputBytes = await fs.readFile(input);
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
  const issues = [], pending_checks = [], records = [];
  for (const section of catalog.sections) {
    let sheet;
    try { sheet = workbook.worksheets.getItem(section.sheet); }
    catch { issue(issues,section.sheet,"", "Required sheet is missing"); continue; }
    const last = column(section.fields.length);
    const expected = ["Business Unit",...section.fields.map(field => field.header)];
    const actual = sheet.getRange(`A4:${last}4`).values[0];
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      issue(issues,section.sheet,`A4:${last}4`,"Headers do not match this skill's intake catalog");
      continue;
    }
    const values = sheet.getRange(`A5:${last}${ROWS+4}`).values;
    const formulas = sheet.getRange(`A5:${last}${ROWS+4}`).formulas;
    const seen = new Set();
    values.forEach((row, rowIndex) => {
      const rowNumber = rowIndex + 5;
      const populated = row.some(value => value !== null && value !== undefined && String(value).trim() !== "");
      if (!populated) return;
      if (formulas?.[rowIndex]?.some(Boolean)) issue(issues,section.sheet,`A${rowNumber}:${last}${rowNumber}`,"Formulas are not accepted in intake rows");
      const businessUnit = typeof row[0] === "string" ? row[0].trim() : "";
      if (!businessUnit) { issue(issues,section.sheet,`A${rowNumber}`,"Business Unit is required"); return; }
      if (seen.has(businessUnit.toLowerCase())) issue(issues,section.sheet,`A${rowNumber}`,"Duplicate Business Unit in this section");
      seen.add(businessUnit.toLowerCase());
      const exportedName = baseline?.business_units.get(businessUnit.toLocaleLowerCase("en-US"));
      if (exportedName && exportedName !== businessUnit) issue(issues,section.sheet,`A${rowNumber}`,`Use the exact exported Business Unit name: ${exportedName}`);
      const operation = baseline ? exportedName ? "edit" : "create" : "unresolved";
      const changes = [];
      section.fields.forEach((field, fieldIndex) => {
        const raw = row[fieldIndex+1];
        if (raw === null || raw === undefined || raw === "") return;
        const value = typeof raw === "string" ? raw.trim() : raw;
        const cell = `${column(fieldIndex+1)}${rowNumber}`;
        if (typeof value === "string" && !value) return;
        if (field.scope === "global" && businessUnit !== catalog.global_business_unit) { issue(issues,section.sheet,cell,"Field is available only for All Business Units"); return; }
        if (field.scope === "specific" && businessUnit === catalog.global_business_unit) { issue(issues,section.sheet,cell,"Field is available only for a specific business unit"); return; }
        if (value === INHERIT) {
          if (businessUnit === catalog.global_business_unit) issue(issues,section.sheet,cell,"All Business Units cannot inherit from itself");
          else { changes.push({key:field.key,label:field.header,mode:"inherit_all"}); issue(pending_checks,section.sheet,cell,"Inheritance needs a supported override-removal operation; omitting the CSV row does not delete the existing business-unit override"); }
          return;
        }
        if (value === catalog.inherit_payables && field.key === "employee_liability_account") {
          changes.push({key:field.key,label:field.header,mode:"inherit_payables"});
          issue(pending_checks,section.sheet,cell,"Confirm FSM representation for Payables account inheritance before import");
          return;
        }
        if (field.kind === "yes_no" && !["Yes","No"].includes(value)) { issue(issues,section.sheet,cell,"Expected Yes or No"); return; }
        if (field.kind === "enum" && !field.choices.some(choice => choice.label === value)) { issue(issues,section.sheet,cell,"Value is not in the source-defined dropdown"); return; }
        if (field.kind === "nonnegative_integer" && (!Number.isSafeInteger(Number(value)) || Number(value) < 0 || String(value).trim() === "")) { issue(issues,section.sheet,cell,"Expected a nonnegative whole number"); return; }
        if (field.kind === "email" && (typeof value !== "string" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))) { issue(issues,section.sheet,cell,"Expected an email address"); return; }
        if (field.kind === "url" && (typeof value !== "string" || !/^https?:\/\/\S+$/i.test(value))) { issue(issues,section.sheet,cell,"Expected an HTTP or HTTPS URL"); return; }
        const choice = field.kind === "enum" ? field.choices.find(item => item.label === value) : null;
        const valueCode = field.kind === "yes_no" ? value === "Yes" ? "Y" : "N" : choice?.code ?? null;
        changes.push({key:field.key,label:field.header,value,source:field.source,code:field.code,valueCode});
        if (field.mapping !== "confirmed" || (field.kind === "enum" && !valueCode)) issue(pending_checks,section.sheet,cell,"Source field or selected value code has no confirmed mapping");
      });
      if (changes.length) {
        records.push({sheet:section.sheet,row:rowNumber,businessUnit,operation,changes});
        if (!baseline) issue(pending_checks,section.sheet,`A${rowNumber}`,"A fresh target setup-data export is required to resolve Create or Edit");
      }
    });
  }
  const readiness = importReadiness(records, issues, pending_checks, baseline);
  if (baseline) await verifyBusinessUnits(records, baseline);
  const result = {schema_version:catalog.schema_version,task_code:catalog.source_export.task_code,source_workbook:input,
    source_workbook_sha256:sha256(inputBytes),
    baseline:baseline ? {directory:baseline.directory,process_id:baseline.process_id,metadata_process_id:baseline.metadata_process_id,environment:baseline.environment,process_date:baseline.process_date,archive_sha256:baseline.archive_sha256,file_sha256:baseline.file_sha256} : null,
    ...readiness,records,issues,pending_checks};
  if (output) {await fs.mkdir(path.dirname(output),{recursive:true}); await fs.writeFile(output,JSON.stringify(result,null,2)+"\n");}
  console.log(JSON.stringify({records:records.length,issues:issues.length,pending_checks:pending_checks.length,ready_for_import:readiness.ready_for_import,output:output??null}));
  if (issues.length) process.exitCode = 2;
}

async function verifyBusinessUnits(records, baseline) {
  const names = [...new Set(records.map(record => record.businessUnit))]
    .filter(name => name !== catalog.global_business_unit);
  if (!names.length) return;
  const evidencePath = valueOf("--reference-evidence");
  if (!evidencePath) throw new Error("--reference-evidence from finBusinessUnitsLOV is required for specific business units");
  const evidence = JSON.parse(await fs.readFile(evidencePath, "utf8"));
  const age = Date.now() - Date.parse(evidence.captured_at);
  if (!sameEnvironment(evidence.environment, baseline.environment) || evidence.baseline_process_id !== baseline.process_id
      || evidence.path !== "/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV"
      || evidence.http_status !== 200 || evidence.complete !== true || !Array.isArray(evidence.items)
      || !/(Z|[+-]\d\d:\d\d)$/.test(evidence.captured_at ?? "") || !Number.isFinite(age) || age < 0 || age > 86400000) {
    throw new Error("Fresh complete same-environment finBusinessUnitsLOV evidence bound to the baseline ProcessId is required");
  }
  for (const name of names) {
    const matches = evidence.items.filter(item => item?.BusinessUnitName === name);
    if (matches.length !== 1 || !matches[0].BusinessUnitId || matches[0].ActiveFlag !== true) {
      throw new Error(`Business Unit ${name}: expected one exact active destination LOV match; found ${matches.length}`);
    }
  }
}

function csvText(rows, newline) {
  return rows.map(row => row.map(value => `"${String(value ?? "").replaceAll("\"", "\"\"")}"`).join(",")).join(newline) + newline;
}

function optionTable(bytes, filename) {
  const text = bytes.toString("utf8");
  const newline = text.includes("\r\n") ? "\r\n" : "\n";
  const rows = csvRows(text.replace(/^\uFEFF/, ""));
  const [header, ...data] = rows;
  const buIndex = header?.indexOf("BuName") ?? -1;
  const optionIndex = header?.indexOf("OptionCode") ?? -1;
  const valueIndex = header?.indexOf("ValueCode") ?? -1;
  if (buIndex < 0 || optionIndex < 0 || valueIndex < 0 || new Set(header).size !== header.length
      || data.some(row => row.length !== header.length)) {
    throw new Error(`${filename} does not have the expected BuName, OptionCode, and ValueCode columns`);
  }
  return {filename, bytes, newline, header, data, buIndex, optionIndex, valueIndex};
}

function selectedOptionRow(table, record, change) {
  const {filename, data, buIndex, optionIndex} = table;
  const matches = data.filter(row => normalizedBusinessUnit(row[buIndex]) === normalizedBusinessUnit(record.businessUnit)
    && row[optionIndex] === change.code);
  if (matches.length > 1) {
    throw new Error(`${filename} must contain at most one row for ${record.businessUnit || catalog.global_business_unit} and ${change.code}; found ${matches.length}`);
  }
  return matches[0] ?? null;
}

function assertPairedOptionRows(setup, cashAdvance, records) {
  if (JSON.stringify(setup.header) !== JSON.stringify(cashAdvance.header)) {
    throw new Error("Paired option CSV headers diverge; obtain a fresh target export");
  }
  for (const record of records) {
    for (const change of record.changes) {
      if (change.source !== "EXM_SETUP_OPTION") continue;
      const setupRow = selectedOptionRow(setup, record, change);
      const cashRow = selectedOptionRow(cashAdvance, record, change);
      if (JSON.stringify(setupRow) !== JSON.stringify(cashRow)) {
        throw new Error(`Paired option rows diverge for ${record.businessUnit || catalog.global_business_unit} and ${change.code}; obtain a fresh target export`);
      }
    }
  }
}

function updateOptionRows(table, records) {
  const {newline, header, data, valueIndex, buIndex, optionIndex} = table;
  const changes = records.flatMap(record => record.changes.filter(change => change.source === "EXM_SETUP_OPTION").map(change => ({record, change})));
  if (!changes.length) return table.bytes;
  for (const {record, change} of changes) {
    let row = selectedOptionRow(table, record, change);
    if (!row) {
      // New overrides are sparse rows, never copies of a global row's IDs,
      // audit attributes, or unrelated settings. The FSM hook resolves OrgId.
      row = header.map(() => "");
      row[buIndex] = record.businessUnit === catalog.global_business_unit ? "" : record.businessUnit;
      row[optionIndex] = change.code;
      if (record.businessUnit === catalog.global_business_unit && header.includes("OtherOrgId")) {
        row[header.indexOf("OtherOrgId")] = "-1";
      }
      data.push(row);
    }
    row[valueIndex] = change.valueCode;
  }
  return Buffer.from(csvText([header, ...data], newline), "utf8");
}

function updateSettingRows(bytes, records) {
  const changes = records.flatMap(record => record.changes.filter(confirmedScalarSetting).map(change => ({record, change})));
  if (!changes.length) return bytes;
  const text = bytes.toString("utf8"), newline = text.includes("\r\n") ? "\r\n" : "\n";
  const [header, ...rows] = csvRows(text.replace(/^\uFEFF/, ""));
  const buIndex = header.indexOf("BuName"), codeIndex = header.indexOf("SettingCode"), valueIndex = header.indexOf("SettingValue");
  if (Math.min(buIndex, codeIndex, valueIndex) < 0 || new Set(header).size !== header.length || rows.some(row => row.length !== header.length)) {
    throw new Error("EXM_ORG_SETTING.csv has an unsupported or malformed schema");
  }
  for (const {record, change} of changes) {
    const matches = rows.filter(row => normalizedBusinessUnit(row[buIndex]) === normalizedBusinessUnit(record.businessUnit) && row[codeIndex] === change.code);
    if (matches.length > 1) throw new Error("Ambiguous business-unit SettingCode rows");
    let row = matches[0];
    if (!row) {
      row = header.map(() => "");
      row[buIndex] = record.businessUnit === catalog.global_business_unit ? "" : record.businessUnit;
      row[codeIndex] = change.code;
      rows.push(row);
    }
    row[valueIndex] = String(change.value);
    const decoded = header.indexOf("SettingValueDecoded");
    if (decoded >= 0) row[decoded] = String(change.value);
  }
  return Buffer.from(csvText([header, ...rows], newline));
}

function crc32(bytes) {
  let value = 0xffffffff;
  for (const byte of bytes) {
    value ^= byte;
    for (let bit = 0; bit < 8; bit++) value = (value >>> 1) ^ (value & 1 ? 0xedb88320 : 0);
  }
  return (value ^ 0xffffffff) >>> 0;
}

function le16(value) {
  const bytes = Buffer.alloc(2); bytes.writeUInt16LE(value); return bytes;
}

function le32(value) {
  const bytes = Buffer.alloc(4); bytes.writeUInt32LE(value >>> 0); return bytes;
}

function storedZip(members) {
  const localParts = [], centralParts = [];
  let offset = 0;
  for (const {name, bytes} of members) {
    const nameBytes = Buffer.from(name, "utf8");
    const checksum = crc32(bytes);
    const local = Buffer.concat([
      le32(0x04034b50), le16(20), le16(0x0800), le16(0), le16(0), le16(0),
      le32(checksum), le32(bytes.length), le32(bytes.length), le16(nameBytes.length), le16(0), nameBytes, bytes,
    ]);
    localParts.push(local);
    centralParts.push(Buffer.concat([
      le32(0x02014b50), le16(20), le16(20), le16(0x0800), le16(0), le16(0), le16(0),
      le32(checksum), le32(bytes.length), le32(bytes.length), le16(nameBytes.length), le16(0), le16(0), le16(0), le16(0),
      le32(0), le32(offset), nameBytes,
    ]));
    offset += local.length;
  }
  const central = Buffer.concat(centralParts);
  return Buffer.concat([...localParts, central, le32(0x06054b50), le16(0), le16(0), le16(members.length), le16(members.length), le32(central.length), le32(offset), le16(0)]);
}

function requiredArgument(flag) {
  const value = valueOf(flag);
  if (!value) throw new Error(`${flag} is required`);
  return value;
}

async function buildImport(validationPath, baselineDirectory, expectedEnvironment, processId, archivePath, output, manifestOutput) {
  if (manifestOutput && path.resolve(output) === path.resolve(manifestOutput)) throw new Error("Package and manifest need distinct output paths");
  for (const target of [output, manifestOutput].filter(Boolean)) {
    try { await fs.access(target); throw new Error(`Refusing to overwrite existing output: ${target}`); }
    catch (error) { if (error.code !== "ENOENT") throw error; }
  }
  const validation = JSON.parse(await fs.readFile(validationPath, "utf8"));
  const baseline = await loadBaseline(baselineDirectory, expectedEnvironment, processId, archivePath);
  if (validation?.task_code !== catalog.source_export.task_code) throw new Error("Validation result does not belong to this setup task");
  if (validation?.ready_for_import !== true) throw new Error("Validation result is not ready for confirmed FSM create/update package preparation");
  if (validation?.baseline?.process_id !== baseline.process_id || !sameEnvironment(validation?.baseline?.environment, baseline.environment) || validation?.baseline?.archive_sha256 !== baseline.archive_sha256) {
    throw new Error("Validation result baseline does not match the requested target export");
  }
  const workbookPath = validation.source_workbook;
  if (typeof workbookPath !== "string" || !validation.source_workbook_sha256) throw new Error("Validation result does not bind a source workbook digest");
  if (sha256(await fs.readFile(workbookPath)) !== validation.source_workbook_sha256) throw new Error("Source workbook changed after validation; validate it again before package preparation");
  for (const [filename, digest] of Object.entries(validation.baseline.file_sha256 ?? {})) {
    if (baseline.file_sha256[filename] !== digest) throw new Error(`Baseline ${filename} changed after validation; export and validate again`);
  }
  if (!Array.isArray(validation.records) || !validation.records.length || !validation.records.every(record => ["edit", "create"].includes(record.operation) && Array.isArray(record.changes) && record.changes.length && record.changes.every(confirmedChange))) {
    throw new Error("Validation result contains an unresolved, inherited, dynamic, or unconfirmed change");
  }
  await verifyBusinessUnits(validation.records, baseline);
  const names = ["ASM_SETUP_CSV_METADATA.xml", "EXM_SETUP_OPTION.csv", "EXM_ORG_SETTING.csv", "EXM_CASH_ADV_SETUP_AND_POLICY.csv"];
  const source = Object.fromEntries(await Promise.all(names.map(async name => [name, await fs.readFile(path.join(baselineDirectory, name))])));
  const setupTable = optionTable(source["EXM_SETUP_OPTION.csv"], "EXM_SETUP_OPTION.csv");
  const cashTable = optionTable(source["EXM_CASH_ADV_SETUP_AND_POLICY.csv"], "EXM_CASH_ADV_SETUP_AND_POLICY.csv");
  assertPairedOptionRows(setupTable, cashTable, validation.records);
  const setupOption = updateOptionRows(setupTable, validation.records);
  const cashAdvance = updateOptionRows(cashTable, validation.records);
  const settings = updateSettingRows(source["EXM_ORG_SETTING.csv"], validation.records);
  const members = names.map(name => ({name, bytes: name === "EXM_SETUP_OPTION.csv" ? setupOption : name === "EXM_CASH_ADV_SETUP_AND_POLICY.csv" ? cashAdvance : name === "EXM_ORG_SETTING.csv" ? settings : source[name]}));
  const archive = storedZip(members);
  await fs.mkdir(path.dirname(output), {recursive:true});
  await fs.writeFile(output, archive, {flag:"wx"});
  const manifest = {
    schema_version: "1.0",
    task_code: catalog.source_export.task_code,
    environment: baseline.environment,
    baseline_process_id: baseline.process_id,
    baseline_archive_sha256: baseline.archive_sha256,
    source_workbook_sha256: validation.source_workbook_sha256,
    baseline_file_sha256: baseline.file_sha256,
    package_sha256: sha256(archive),
    package_members: names,
    records: validation.records,
    next_action: "Submit the unchanged package only through core.data-loader after its preflight, Task Hook validation, and explicit approval."
  };
  if (manifestOutput) {
    await fs.mkdir(path.dirname(manifestOutput), {recursive:true});
    await fs.writeFile(manifestOutput, JSON.stringify(manifest, null, 2) + "\n", {flag:"wx"});
  }
  console.log(JSON.stringify({output,manifest_output:manifestOutput ?? null,records:validation.records.length,package_sha256:manifest.package_sha256,ready_for_core_data_loader:true}));
}

const [command,...args] = process.argv.slice(2);
function valueOf(flag) {const i=args.indexOf(flag); return i<0 ? null : args[i+1];}
const usage = `Usage: node expense_system_options_intake.mjs COMMAND
  create --output FILE.xlsx
  validate --input FILE.xlsx [--baseline-dir EXTRACTED_DATA_EXPORT --baseline-process-id ID --baseline-archive EXPORT.zip --environment NAME --reference-evidence BU_EVIDENCE.json] [--output REPORT.json]
  build-import --validation REPORT.json --baseline-dir EXTRACTED_DATA_EXPORT --baseline-process-id ID --baseline-archive EXPORT.zip --environment NAME --reference-evidence BU_EVIDENCE.json --output PACKAGE.zip [--manifest-output MANIFEST.json]
--reference-evidence is required for specific Business Units in validate and build-import; All Business Units alone does not require it.
Use --help to show this usage without creating or validating artifacts.`;
try {
  if (["--help", "-h", "help"].includes(command)) console.log(usage);
  else if (command === "create" && valueOf("--output")) await create(path.resolve(valueOf("--output")));
  else if (command === "validate" && valueOf("--input")) {
    const baseline = valueOf("--baseline-dir") ? await loadBaseline(path.resolve(valueOf("--baseline-dir")),valueOf("--environment"),valueOf("--baseline-process-id"),valueOf("--baseline-archive") ? path.resolve(valueOf("--baseline-archive")) : null) : null;
    await validate(path.resolve(valueOf("--input")),valueOf("--output") ? path.resolve(valueOf("--output")) : null,baseline);
  }
  else if (command === "build-import") {
    await buildImport(path.resolve(requiredArgument("--validation")), path.resolve(requiredArgument("--baseline-dir")), requiredArgument("--environment"), requiredArgument("--baseline-process-id"), valueOf("--baseline-archive") ? path.resolve(valueOf("--baseline-archive")) : null, path.resolve(requiredArgument("--output")), valueOf("--manifest-output") ? path.resolve(valueOf("--manifest-output")) : null);
  }
  else {console.error(usage); process.exitCode=2;}
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  const failure_class = /ENOENT|EACCES|EPERM/.test(message) ? "artifact persistence"
    : /metadata|BuName|baseline CSV|template export|Baseline archive|Baseline .* changed/.test(message) ? "catalog mismatch" : "input validation";
  const stage = command === "validate" ? "baseline-and-intake-validation" : command === "build-import" ? "confirmed-fsm-create-update-package-preparation" : "workbook-creation";
  console.error(JSON.stringify({status:"failed",stage,failure_class,message}));
  process.exitCode = 2;
}
