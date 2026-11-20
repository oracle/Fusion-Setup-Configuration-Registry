"""Read the Corporate Card Program input workbook; local parsing only."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile
import xml.etree.ElementTree as ET
from prepare_fsm_package import ALLOWED, ROOT, COMPANY, UPLOAD, PARENT

SHEETS = {'Program': ROOT, 'Company Account': COMPANY, 'Upload Rule': UPLOAD}
FIELDS = {name: (PARENT + sorted(ALLOWED[entity] - set(PARENT)) if entity == ROOT else sorted(ALLOWED[entity])) for name, entity in SHEETS.items()}
NS = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
LEGACY = {
    'Program': {8:'request.operation',9:'request.environment',10:'request.objective',11:'request.expected_result',12:'request.existing_program',15:'CardProgramName',16:'CardTypeLookupCode',17:'CardBrandLookupCode',18:'Description',19:'InactiveDate',20:'EnableCcTokenFlag'},
    'Company Accounts': dict(enumerate(['CompanyAccountName','BuName','PayablesBUName','CardIssuerName','CardIssuerSiteName','CompanyNumber','BillingCntlAcctNumber','CardAdminName','PaymentTermName','PaymentCurrencyCode','PaymentDueFromCode','ExpenseCcidSegments','PayGroupCode','InclPersonalExpenseFlag','OverlayBalancingSegFlag','InactiveDate'],9)),
    'Processing Settings': dict(zip(list(range(9,17))+list(range(19,25)),['FileFormatCode','DetailWaitingDuration','CardEmpMatchingRule','MatchEmployeeAcrossBu','CcExpTypSumSourceCol','CcExpTypDtlSourceCol','MapTypeCode','MapTypeCode1','DownloadProfileName','Server','RemoteFilename','SecureDirectory','PgpEncryptionAlias','PgpSignatureAlias']))
}


def legacy_values(name, cells):
    entity = {'Program':ROOT,'Company Accounts':COMPANY,'Processing Settings':UPLOAD}[name]
    values = {}; locations = {}; request = {}
    for row, field in LEGACY[name].items():
        if cells.get('E'+str(row)) != field:
            raise ValueError(name+': changed legacy field reference')
        address='B'+str(row); value=cells.get(address,'')
        if cells.get('C'+str(row),'').strip():
            raise ValueError(name+': explicit field actions require review; CREATE supports values only')
        if not value.strip(): continue
        if field.startswith('request.'):
            request[field]=value
        elif field not in ALLOWED[entity]:
            raise ValueError(name+'!'+address+': populated field is outside supported CREATE scope')
        else:
            values[field]=value; locations[field]=name+'!'+address
    if name == 'Program':
        if request.get('request.operation','Create').strip().upper() != 'CREATE' or request.get('request.existing_program'):
            raise ValueError('Only a new CREATE program is supported')
        if any(cells.get(col+str(row),'').strip() for row in range(24,29) for col in 'ABCDE'):
            raise ValueError('Additional requests require explicit scope review')
    if name == 'Company Accounts':
        for row, field in LEGACY[name].items():
            if cells.get('E'+str(row+18)) != field:
                raise ValueError('Changed second-account field reference')
        if any(cells.get(col+str(row),'').strip() for row in range(27,43) for col in 'BC'):
            raise ValueError('Only one company account is supported')
    return entity, values, locations, request


REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def parse_workbook(path):
    raw = Path(path).read_bytes()
    if len(raw) > 10_000_000: raise ValueError('Workbook exceeds 10 MB')
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or sum(i.file_size for i in z.infolist()) > 30_000_000:
            raise ValueError('Invalid or oversized workbook')
        for name in names:
            if name.startswith('/') or '..' in PurePosixPath(name).parts or '\\' in name:
                raise ValueError('Unsafe workbook member')
            if any(v in name.lower() for v in ('vbaproject','externallink','embeddings/','connections.xml','querytables/')):
                raise ValueError('Active or linked workbook content is unsupported')
        def xml(name):
            content = z.read(name)
            if b'<!DOCTYPE' in content.upper() or b'<!ENTITY' in content.upper(): raise ValueError('Unsafe workbook XML')
            return ET.fromstring(content)
        for name in names:
            if name.endswith('.rels') and any(r.get('TargetMode') == 'External' and not r.get('Type','').endswith('/relationships/hyperlink') for r in xml(name)):
                raise ValueError('External workbook relationships are unsupported')
        strings = []
        if 'xl/sharedStrings.xml' in names:
            strings = [''.join(t.text or '' for t in s.findall('.//s:t',NS)) for s in xml('xl/sharedStrings.xml').findall('s:si',NS)]
        relationships = {r.get('Id'):r.get('Target') for r in xml('xl/_rels/workbook.xml.rels')}
        sheets = xml('xl/workbook.xml').findall('s:sheets/s:sheet',NS)
        legacy = {s.get('name') for s in sheets} == set(LEGACY)
        if len(sheets) != 3 or (not legacy and {s.get('name') for s in sheets} != set(SHEETS)):
            raise ValueError('Use Program, Company Account and Upload Rule sheets from the template')
        result = {'operation':'CREATE','rows':{}}; provenance = {}; request_metadata = {}
        for sheet in sheets:
            name = sheet.get('name')
            if sheet.get('state','visible') != 'visible': raise ValueError('Hidden input sheets are unsupported')
            target = relationships.get(sheet.get(REL),'')
            member = target.lstrip('/') if target.startswith('/') else 'xl/'+target
            if '..' in PurePosixPath(member).parts or not member.startswith('xl/worksheets/'):
                raise ValueError('Unsafe sheet relationship')
            cells = {}
            for c in xml(member).findall('.//s:sheetData/s:row/s:c',NS):
                address = c.get('r','')
                if not re.fullmatch('[A-Z]+[1-9][0-9]*',address) or address in cells: raise ValueError('Invalid cell address')
                if c.find('s:f',NS) is not None:
                    if legacy and name == 'Program' and address == 'B5': continue  # decorative review formula; never evaluate or use as readiness
                    raise ValueError(name+'!'+address+': formulas are unsupported')
                typ=c.get('t'); val=c.find('s:v',NS); text='' if val is None else val.text or ''
                if typ == 's':
                    if not text.isdigit() or int(text)>=len(strings): raise ValueError('Invalid shared string')
                    text=strings[int(text)]
                elif typ == 'inlineStr': text=''.join(t.text or '' for t in c.findall('.//s:t',NS))
                elif text and typ != 'str': raise ValueError(name+'!'+address+': enter literal text to preserve identifiers and leading zeros')
                cells[address]=text
            if legacy:
                entity, values, locations, request = legacy_values(name, cells)
                request_metadata.update(request)
                if entity == ROOT or values:
                    result['rows'][entity]=values; provenance[entity]=locations
                continue
            fields = FIELDS[name]
            values = {}; locations = {}
            for address, text in cells.items():
                match=re.fullmatch('([A-Z]+)([0-9]+)',address); index=0
                for char in match[1]: index=index*26+ord(char)-64
                row=int(match[2])
                if row==1:
                    if index>len(fields) or text!=fields[index-1]: raise ValueError(name+': changed template header')
                elif text.strip():
                    if row!=2 or index>len(fields): raise ValueError(name+'!'+address+': only one program and one row per child are supported')
                    values[fields[index-1]]=text; locations[fields[index-1]]=name+'!'+address
            if len([a for a in cells if re.fullmatch('[A-Z]+1',a)]) != len(fields): raise ValueError(name+': missing headers')
            if name=='Program' or values:
                result['rows'][SHEETS[name]]=values; provenance[SHEETS[name]]=locations
        return result, {'status':'PARSED','sourceSha256':hashlib.sha256(raw).hexdigest(),
                        'layout':'legacy' if legacy else 'canonical', 'requestMetadata':request_metadata,
                        'cellProvenance':provenance,'importReady':False,'importAuthorized':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('workbook',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try:
        design,report=parse_workbook(args.workbook)
        with args.output.open('x') as f: json.dump(design,f,indent=2)
        print(json.dumps(report,indent=2));return 0
    except (ValueError,OSError,KeyError,zipfile.BadZipFile,ET.ParseError) as e:
        print(json.dumps({'status':'BLOCKED','failure_class':'input_validation','message':str(e)}));return 2

if __name__=='__main__':raise SystemExit(main())
