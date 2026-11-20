"""Mileage source-qualified no-determinant create and existing update state."""
import hashlib
from pathlib import Path
from accepted_meals_profile import decimal_value, rate_date
from mileage_rate_profile import P, R, IDENTITY, validate_rate

ROOT=Path(__file__).resolve().parents[1]
SOURCE='MILEAGE-SOURCE-CONTRACT'
FLAGS=('EnabledStdDeductionFlag','EnabledEligibilityFlag','EnabledDeductCommuteFlag',
       'EnabledPassengerFlag','CapturePassNamesFlag','CalcPassRateByDistFlag',
       'EnabledMaxPassFlag','EnabledAdditnlRatesFlag')
DETERMINANTS=('EnabledRoleFlag','EnabledLocationFlag','DistanceThresholdFlag',
              'EnabledVehCategoryFlag','EnabledVehTypeFlag','EnabledFuelTypeFlag','EnabledGenderFlag')
CONTEXT=('PolicyRoleCode','LocationTypeCode','ZoneTypeCode','ApplyThresholdByCode',
         'VehicleCategoryListCode','VehicleTypeListCode','FuelTypeListCode')
UPDATES={'Description','CountryCode','UnitOfMeasureCode','MileageDeduction','EligibilityDistance',
         'CommuteDistanceRequiredFlag','PassengerRuleCode','MaximumPassengers','AdditionalRatesListCode',*FLAGS}

def validate_evidence(contract):
    if contract.get('sources',{}).get(SOURCE,{}).get('sha256')!=hashlib.sha256((ROOT/'references/mileage-source-contract.json').read_bytes()).hexdigest():
        raise ValueError('Mileage source contract changed; regenerate and review runtime')
    if contract.get('sources',{}).get('MILEAGE-CREATE-SERIALIZATION',{}).get('sha256')!=hashlib.sha256((ROOT/'references/mileage-create-serialization.json').read_bytes()).hexdigest():
        raise ValueError('Mileage create serialization changed; regenerate and review runtime')
    from mileage_company_lookup import validate_evidence as validate_company_evidence
    validate_company_evidence(contract)

def whole(value,field,minimum=0,maximum=None):
    number=decimal_value(value,field)
    if number is None or number!=number.to_integral_value() or number<minimum or maximum is not None and number>maximum:
        raise ValueError(field+' requires a whole number in its source-supported range')
    return number

def validate_parent(row):
    if row.get('Status') not in {'DRAFT','VALID'}:
        raise ValueError('Mileage status/lifecycle changes remain separately qualified')
    if not row.get('PolicyName','').strip() or len(row['PolicyName'])>60 or len(row.get('Description',''))>240:
        raise ValueError('Mileage Policy Name allows 60 characters and Description allows 240')
    if row.get('CurrencyOptionCode')!='SINGLE' or not row.get('CurrencyCode'):
        raise ValueError('Mileage requires its resolved single currency')
    for field in DETERMINANTS:
        if row.get(field)!='N':raise ValueError('Mileage requires explicit No for determinant '+field)
    for field in CONTEXT:
        if row.get(field) not in ('',None):raise ValueError('Mileage determinant context is outside initial scope: '+field)
    if row.get('UnitOfMeasureCode') not in {'MILE','KILOMETER','SWEDISH_MILE'}:
        raise ValueError('Mileage Unit of Measure requires an explicit supported selection and target lookup')
    for field in FLAGS:
        if row.get(field) not in ('Y','N',''):
            raise ValueError('Mileage '+field+' must retain a source-backed Yes/No or empty inactive value')
    for flag,amount in [('EnabledStdDeductionFlag','MileageDeduction'),('EnabledEligibilityFlag','EligibilityDistance')]:
        if row.get(flag)=='Y':whole(row.get(amount,''),amount)
        elif row.get(amount) not in ('',None):whole(row[amount],amount)
    if row.get('CommuteDistanceRequiredFlag') not in {'ORA_EXM_OPTIONAL','ORA_EXM_REQUIRED'}:
        raise ValueError('Commute deduction uses ORA_EXM_OPTIONAL/REQUIRED package codes, not Y/N')
    if row.get('EnabledPassengerFlag')=='Y':
        if row.get('PassengerRuleCode') not in {'SINGLE','RANGE'}:
            raise ValueError('Mileage passenger rules requiring determinants are outside initial scope')
        if row.get('EnabledMaxPassFlag')=='Y':whole(row.get('MaximumPassengers',''),'MaximumPassengers',1,999)
    elif row.get('PassengerRuleCode') not in ('',None):
        raise ValueError('Disabled passenger rates require empty Passenger Rate Type; no automatic clearing')
    if row.get('MaximumPassengers') not in ('',None):whole(row['MaximumPassengers'],'MaximumPassengers',1,999)
    if row.get('EnabledAdditnlRatesFlag')=='Y' and not row.get('AdditionalRatesListCode'):
        raise ValueError('Company-specific rates require the exact selected lookup type')
    # Dynamic type/code eligibility is enforced separately by lookup preflight;
    # a local label, observed value or standard EXM lookup cannot substitute.

def validate_schedule(parent,rates):
    validate_parent(parent)
    if not rates:raise ValueError('Mileage policy requires compatible rates')
    keys=set();groups={}
    for row in rates:
        validate_rate(row,parent)
        if row.get('InvalidCode') not in ('',None):raise ValueError('Mileage invalid rate cannot enter update preparation')
        key=tuple(row.get(f,'') for f in IDENTITY if f!='StartDate')
        if key in keys:raise ValueError('Duplicate Mileage alternate key excluding StartDate')
        keys.add(key)
        group=tuple(row.get(f,'') for f in IDENTITY if f not in {'StartDate','EndDate'})
        groups.setdefault(group,[]).append((rate_date(row['StartDate'],'StartDate'),rate_date(row['EndDate'],'EndDate') if row.get('EndDate') else None))
        if row['TypeOfRateCode']=='PASSENGER':
            threshold=row.get('PassengerThreshold','')
            if parent['PassengerRuleCode']=='SINGLE' and threshold not in ('',None):
                raise ValueError('Single passenger rate retains a blank range coordinate')
            if parent['PassengerRuleCode']=='RANGE' and threshold in ('',None):
                raise ValueError('Passenger ranges require an explicit range coordinate; no inferred sentinel')
    for periods in groups.values():
        periods.sort()
        if any(left[1] is None or right[0]<=left[1] for left,right in zip(periods,periods[1:])):
            raise ValueError('Mileage effective periods overlap; end dates are inclusive')
    if not any(r['TypeOfRateCode']=='MILEAGE' for r in rates):raise ValueError('Mileage policy requires its base mileage rate')
    if parent.get('EnabledPassengerFlag')=='Y' and not any(r['TypeOfRateCode']=='PASSENGER' for r in rates):
        raise ValueError('Enabled passenger option requires compatible passenger rates')
    if parent.get('EnabledAdditnlRatesFlag')=='Y' and not any(r['TypeOfRateCode']=='ADDITIONAL' for r in rates):
        raise ValueError('Enabled company-specific option requires compatible rates and qualified dynamic references')

def validate_selection(records,rows):
    for name in {r['policy_name'] for r in records}:
        parents=[r for r in rows[P] if r['PolicyName'].casefold()==name.casefold()]
        rates=[r for r in rows[R] if r[P+'.PolicyName'].casefold()==name.casefold()]
        if len(parents)>1 or parents and parents[0]['PolicyName']!=name or any(r[P+'.PolicyName']!=name for r in rates):
            raise ValueError('Mileage requires an exact unambiguous parent association')
        if parents:validate_schedule(parents[0],rates)
        elif rates:raise ValueError('Orphan Mileage baseline rate')
        elif {r['entity']for r in records if r['policy_name']==name}!={P,R}:
            raise ValueError('Create requires a Mileage parent and at least one base rate')

def validate_pre_edit_selection(records,rows):
    """Bind old identities/hard scope, without demanding old business values.

    The source import resolves AltKeys before readXML. Requiring an old Rate,
    tolerance or other writable value already to be complete was a local
    preparation restriction, not source-proven update behavior.
    """
    for name in {r['policy_name'] for r in records}:
        parents=[r for r in rows[P] if r['PolicyName'].casefold()==name.casefold()]
        rates=[r for r in rows[R] if r[P+'.PolicyName'].casefold()==name.casefold()]
        if len(parents)>1 or parents and parents[0]['PolicyName']!=name or any(r[P+'.PolicyName']!=name for r in rates):
            raise ValueError('Mileage requires its exact unambiguous existing parent')
        if not parents:
            if rates:raise ValueError('Orphan Mileage baseline rate')
            if {r['entity']for r in records if r['policy_name']==name}!={P,R}:
                raise ValueError('Create requires a Mileage parent and at least one base rate')
            continue
        parent=parents[0]
        if (parent.get('Status') not in {'DRAFT','VALID'} or not name.strip() or len(name)>60
                or parent.get('CurrencyOptionCode')!='SINGLE' or not parent.get('CurrencyCode')):
            raise ValueError('Mileage pre-edit lifecycle, identity or existing currency scope is unqualified')
        if any(parent.get(f)!='N' for f in DETERMINANTS) or any(parent.get(f) not in ('',None) for f in CONTEXT):
            raise ValueError('Mileage pre-edit determinant scope remains excluded')
        keys,no_start=set(),set()
        for row in rates:
            validate_rate(row,parent,require_amount=False,validate_applicability=False)
            if row.get('InvalidCode') not in ('',None):
                raise ValueError('Mileage invalid rate cannot enter update preparation')
            key=tuple(row.get(f,'') for f in IDENTITY)
            other=tuple(row.get(f,'') for f in IDENTITY if f!='StartDate')
            if key in keys or other in no_start:
                raise ValueError('Ambiguous Mileage full or no-Start alternate key')
            keys.add(key);no_start.add(other)

def validate_change(entity,operation,before,after,baseline_rows):
    if operation not in {'create','update'}:raise ValueError('Mileage requires a reviewed create or update operation')
    if operation=='create' and after.get('Status')!='DRAFT':raise ValueError('Mileage create requires explicit managed DRAFT status')
    allowed=UPDATES if entity==P else {'Rate'}
    if operation=='update' and {f for f in after if after[f]!=before[f]}-allowed:
        raise ValueError('Mileage keys, currency, dates, audit, status and determinant writes are not eligible field overrides')
    if entity==P:
        validate_parent(after)
        if operation=='create' and any(after.get(flag)not in {'Y','N'}for flag in FLAGS):
            raise ValueError('Mileage create requires explicit Yes/No for every eligibility/add-on control')
        dependencies={'MileageDeduction':'EnabledStdDeductionFlag','EligibilityDistance':'EnabledEligibilityFlag',
            'CommuteDistanceRequiredFlag':'EnabledDeductCommuteFlag','PassengerRuleCode':'EnabledPassengerFlag',
            'CapturePassNamesFlag':'EnabledPassengerFlag','CalcPassRateByDistFlag':'EnabledPassengerFlag',
            'EnabledMaxPassFlag':'EnabledPassengerFlag','MaximumPassengers':'EnabledMaxPassFlag',
            'AdditionalRatesListCode':'EnabledAdditnlRatesFlag'}
        for field,flag in dependencies.items():
            if operation=='create' and field=='CommuteDistanceRequiredFlag' and after[field]=='ORA_EXM_OPTIONAL' and after[flag]=='N':
                continue  # Explicit inactive package code, not an inferred raw N/default.
            if after.get(field)!=before.get(field) and after.get(field) not in ('','N') and after.get(flag)!='Y':
                raise ValueError('Mileage supplied '+field+' requires '+flag+' enabled')
    else:
        parents=[p for p in baseline_rows[P] if p['PolicyName']==after[P+'.PolicyName']]
        if not parents and operation=='create':
            return  # Complete new parent/rate state is checked after every overlay.
        if len(parents)!=1:raise ValueError('Mileage line requires exact existing parent')
        # Parent business controls may be corrected in the same workbook. Their
        # resulting applicability is checked only after all overlays.
        validate_rate(after,parents[0],validate_applicability=False)

def verify_result(submitted,original_rows):
    names={r['values'].get('PolicyName',r['values'].get(P+'.PolicyName')) for r in submitted}
    validate_pre_edit_selection([{'entity':r['entity'],'policy_name':r['values'].get('PolicyName',r['values'].get(P+'.PolicyName'))}for r in submitted],original_rows)
    parents={r['PolicyName']:r for r in original_rows[P]}
    rates={tuple(r.get(f,'') for f in IDENTITY):r for r in original_rows[R]}
    seen=set();created=False
    for record in submitted:
        row=record['values'];name=row.get('PolicyName',row.get(P+'.PolicyName'));names.add(name)
        target=parents if record['entity']==P else rates
        key=name if record['entity']==P else tuple(row.get(f,'') for f in IDENTITY)
        if (record['entity'],key) in seen:
            raise ValueError('Mileage resulting state requires one immutable identity per submitted row')
        operation='update'if key in target else'create'
        created=created or operation=='create'
        validate_change(record['entity'],operation,target.get(key,{}),row,original_rows)
        seen.add((record['entity'],key));target[key]=row
    for name in names:
        if name not in parents:raise ValueError('Mileage rate parent missing')
        validate_schedule(parents[name],[r for r in rates.values() if r[P+'.PolicyName']==name])
    return {'profile':'mileage-no-determinants-source-v1','requires_live_qualification':True,
            'qualification':('source_qualified_create_preparation_target_and_live_pending'if created else'source_reviewed_updates_require_exact_field_acceptance_and_live_reconciliation'),'import_approved':False}
