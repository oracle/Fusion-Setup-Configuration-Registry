"""Offline, task-owned checks over the exact bytes submitted for approval.

No defaults are injected. Operation is caller-declared: an update identifies an
existing parent and may explicitly insert children. Identity intent, privileges
and server validation remain deferred to preparation and the governed workflow.
Column inventory: completed 2026-09-17 FSM template export (request 52108).
Requiredness: PlanningOptionEO, PlanTypeEO and AmountSetEO source inspection;
see the task's defaulting matrix for scoped evidence and default provenance.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import io
import json
import re
from pathlib import Path
import stat
import xml.etree.ElementTree as ET
import zipfile

PARENT = 'PJO_PLAN_TYPE_PROJECT.csv'
CHILD = 'PJO_PPT_PLAN_OPTION_GEN_OPT.csv'
LINK = 'PJO_PLAN_TYPE_PROJECT.Name'
CURRENCY = 'PJO_PPT_PLAN_OPTION_CUR_SETTING.csv'
RATES = 'PJO_PPT_PLAN_OPTION_RATE_SCH.csv'
META = 'ASM_SETUP_CSV_METADATA.xml'
TASK = 'PJO_MANAGE_PROJECT_PLAN_TYPES'
COLUMNS = json.loads(Path(__file__).with_name('import_columns.json').read_text())
AMOUNT_FIELDS = tuple('AmountSetTypeCode AllQtyFlag BillRateFlag BrdndRateFlag BrdndCostFlag CostRateFlag RawCostFlag RevenueFlag RevenueQtyFlag CostQtyFlag'.split())
PARENT_REQUIRED = tuple('Name StartDate PlanTypeCode PlanClassCode PlanOptionCode PlanInMultiCurrFlag EnableWfFlag DefaultFinPlanTypeFlag AutoApproveFlag DefaultAwdFinPlanTypeFlag'.split())
CHILD_REQUIRED = tuple('PlanOptionLevelCode ObjectTypeCode PlannedForCode PlanTypeCode PlanInMultiCurrFlag AllowFcstAmtCarryFlag FactorByCode SpecPcRevAtProjLevel SpecPfcRevAtProjLevel SpecPcCostAtProjLevel SpecPfcCostAtProjLevel SyncTaskTxnPlanDates GenBdgtDuringBaseline AutoBdgtBaseline UseThirdPartySoftware AutoRollupTaskDate RaTaskDatesSame UsePlanningRatesFlag EnableCostsForProjPlan AllowNegEtcFlag ProgAutoApprFcstVer ProgAutoGenFcstVer ProgUpdPlanQtyWithEac AmountSetTypeCode RawCostFlag CostQtyFlag RevenueFlag RevenueQtyFlag BrdndCostFlag'.split())
# Explicitly enumerated contracts: a spelling that looks Boolean is insufficient.
YES_NO = set('PlanInMultiCurrFlag EnableWfFlag DefaultFinPlanTypeFlag AutoApproveFlag DefaultAwdFinPlanTypeFlag AllowFcstAmtCarryFlag SpecPcRevAtProjLevel SpecPfcRevAtProjLevel SpecPcCostAtProjLevel SpecPfcCostAtProjLevel SyncTaskTxnPlanDates GenBdgtDuringBaseline AutoBdgtBaseline UseThirdPartySoftware AutoRollupTaskDate RaTaskDatesSame UsePlanningRatesFlag EnableCostsForProjPlan AllowNegEtcFlag ProgAutoApprFcstVer ProgAutoGenFcstVer ProgUpdPlanQtyWithEac RawCostFlag CostQtyFlag RevenueFlag RevenueQtyFlag BrdndCostFlag EnableRevForProjPlan GenInclOpencommFlag GenRetManLineFlag ManualSpreadFlag MapActSummaryFlag'.split())
YES_NO.update(set(AMOUNT_FIELDS) - {'AmountSetTypeCode'})
YES_NO.add('AutoPlanAsmtFlag')
YES_NO.add('AsgnResInSingleCurrFlag')
CONVERSION_PREFIXES = ('PcCost', 'PcRev', 'PfcCost', 'PfcRev', 'RateSchCost', 'RateSchRev')


def shared_conversion_intent(source_input):
    """Read the original control without inferring intent from matching rates."""
    if source_input is None:
        return None
    if not isinstance(source_input, dict):
        raise ValueError('SOURCE_INTENT_INVALID: sourceInput must be one business-input object.')
    value = source_input.get('Curr_Set_Use_Conversion')
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in {'true', 'false'}:
        return value.strip().lower() == 'true'
    raise ValueError('SOURCE_INTENT_INVALID: Curr_Set_Use_Conversion must be true or false.')


def validate_source_intent(content, source_input):
    """Reconcile the transient shared-copy intent against persistent ZIP values."""
    if shared_conversion_intent(source_input) is not True:
        return
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        if any(member not in archive.namelist() for member in (PARENT, CHILD)):
            raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion requires parent and options rows.')
        tables = {member: list(csv.DictReader(io.StringIO(archive.read(member).decode('utf-8-sig'))))
                  for member in (PARENT, CHILD)}
    if len(tables[PARENT]) != 1:
        raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion requires one parent.')
    if tables[PARENT][0].get('PlanOptionCode') != 'COST_ONLY':
        raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion supports the evidenced COST_ONLY branch.')
    options = [r for r in tables[CHILD] if r.get('PlannedForCode') == 'COST']
    if len(options) != 1 or options[0].get('EnableCostsForProjPlan') != 'Y':
        raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion requires cost-enabled options.')
    row = options[0]
    if row.get('PlanOptionLevelCode') != 'PLAN_TYPE' or row.get('PlanTypeCode') != 'PROJECT_PLAN':
        raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion requires PROJECT_PLAN at PLAN_TYPE.')
    source = 'Pc' if tables[PARENT][0].get('PlanInMultiCurrFlag') == 'Y' else 'Pfc'
    if not all(row.get(source+'Cost'+suffix) for suffix in ('RateType', 'RateDateType')):
        raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion source attributes are missing.')
    for amount in ('Cost', 'Rev'):
        for dest in (('Pfc', 'RateSch') if source == 'Pc' else ('RateSch',)):
            for suffix in ('RateType', 'RateDateType', 'RateDate'):
                if row.get(dest+amount+suffix, '') != row.get(source+amount+suffix, ''):
                    raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion was not applied to '+dest+amount+suffix)
        if source == 'Pc' and row.get('SpecPfc'+amount+'AtProjLevel', '') != row.get('SpecPc'+amount+'AtProjLevel', ''):
            raise ValueError('SOURCE_INTENT_MISMATCH: Shared conversion override flags differ.')
DOMAINS = {
    'PlanTypeCode': {'PROJECT_PLAN'}, 'PlanClassCode': {'BUDGET'},
    'PlanOptionLevelCode': {'PLAN_TYPE'},
    'ObjectTypeCode': {'PROJECT'},
    'PlanOptionCode': {'COST_ONLY', 'REVENUE_ONLY', 'COST_AND_REV_SEP', 'COST_AND_REV_TOGETHER'},
    'PlannedForCode': {'COST', 'REVENUE', 'COST_AND_REV_TOGETHER'},
    'TimePhasedCode': {'G', 'P', 'N'}, 'PlanLevelCode': {'A', 'P', 'T'},
    'FactorByCode': {'1', '10', '100', '1000', '10000', '100000', '1000000'},
    'PercentCompCalcMethod': {'COST', 'EFFORT', 'MANUAL', 'ORA_OUTPUT_UNITS'},
    'PercentCompRollupMethod': {'COST', 'EFFORT', 'MANUAL'},
    'EtcMethodCode': {'MANUAL', 'REMAINING_PLAN'},
    'RevClassificationMethod': {'CONTRACT', 'MANUAL', 'RATE_BASED'},
}
DOMAINS.update({prefix+'RateDateType': {'FIXED_DATE', 'START_DATE_PRJ_PLAN', 'END_DATE_PRJ_PLAN'}
                for prefix in CONVERSION_PREFIXES})


def validate_archive(content: bytes, *, operation: str) -> dict:
    """Return independent integrity/contract/deferred/server outcomes; never write."""
    integrity, findings = [], []
    result = {
        'archiveSha256': hashlib.sha256(content).hexdigest(),
        'packageIntegrity': {'status': 'passed', 'findings': integrity},
        'taskContractValidation': {'status': 'passed', 'findings': findings},
        'deferredChecks': [
            {'code': 'TARGET_REFERENCES', 'status': 'deferred', 'message': 'Target reference membership, feature state, authorization and protected-record editability require the declared workflow.'},
            {'code': 'UPDATE_IDENTITY', 'status': 'deferred', 'message': 'For update, verify the parent and changed child identities exist and explicitly inserted child identities are absent in the fresh baseline. No omitted values are defaulted locally; every submitted options row needs the full retained amount tuple. Separate parent creates from parent updates.'},
        ],
        'serverValidation': {'status': 'not_run', 'message': 'Local checks do not claim Fusion acceptance.'},
    }

    def issue(code, message, member=None, row=None, attribute=None, *, package=False):
        item = {'code': code, 'message': message, 'blocking': True}
        item.update({k: v for k, v in {'member': member, 'row': row, 'attribute': attribute}.items() if v is not None})
        (integrity if package else findings).append(item)

    def finish():
        result['packageIntegrity']['status'] = 'blocked' if integrity else 'passed'
        result['taskContractValidation']['status'] = 'blocked' if integrity or findings else 'passed'
        return result

    if operation not in {'create', 'update'}:
        issue('OPERATION_UNRESOLVED', 'Declare create or update before validating; upsert cannot establish omitted-field semantics.')
    tables = {}
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            entries = archive.infolist()
            names = [e.filename for e in entries]
            if len(names) != len(set(names)):
                issue('DUPLICATE_MEMBER', 'Duplicate ZIP member names are ambiguous.', package=True)
            if len(entries) > 32 or sum(e.file_size for e in entries) > 32 * 1024 * 1024:
                issue('PACKAGE_LIMIT', 'Package exceeds 32 members or 32 MiB uncompressed.', package=True)
                return finish()
            for entry in entries:
                n = entry.filename
                if n not in COLUMNS and n != META:
                    issue('UNSUPPORTED_MEMBER', 'Expected flat task CSV members and metadata only.', n, package=True)
                    continue
                if stat.S_ISLNK(entry.external_attr >> 16) or entry.flag_bits & 1:
                    issue('UNSAFE_MEMBER', 'Links and encrypted members are unsupported.', n, package=True)
                    continue
                data = archive.read(entry)
                if n == META:
                    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
                        issue('UNSAFE_XML', 'Metadata entity declarations are unsupported.', n, package=True)
                        continue
                    root = ET.fromstring(data)
                    identities = [e.text for e in root.iter() if e.tag.split('}')[-1] == 'ObjectShortName']
                    if identities != [TASK]:
                        issue('TASK_IDENTITY', 'Metadata must identify exactly '+TASK+'.', n, package=True)
                    continue
                reader = csv.reader(io.StringIO(data.decode('utf-8-sig'), newline=''), strict=True)
                headers = next(reader, [])
                if not headers or len(headers) != len(set(headers)) or any(h not in COLUMNS[n] for h in headers):
                    issue('CSV_HEADERS', 'Missing, duplicate or unknown CSV headers.', n, package=True)
                    continue
                rows, seen = [], set()
                for number, cells in enumerate(reader, 2):
                    if not cells:
                        continue  # Exported header-only members include empty lines.
                    if len(cells) != len(headers):
                        issue('CSV_ROW_WIDTH', 'Row width must equal header width.', n, number, package=True)
                        continue
                    if tuple(cells) in seen:
                        issue('DUPLICATE_ROW', 'Repeated CSV row.', n, number, package=True)
                    seen.add(tuple(cells))
                    rows.append((number, dict(zip(headers, cells))))
                tables[n] = rows
            if META not in names:
                issue('MISSING_METADATA', 'Task metadata is required.', META, package=True)
    except (zipfile.BadZipFile, UnicodeError, csv.Error, ET.ParseError, RuntimeError, NotImplementedError, OSError, ValueError) as exc:
        issue('MALFORMED_PACKAGE', str(exc), package=True)
    if integrity:
        return finish()
    if not tables.get(PARENT):
        issue('MISSING_PARENT', 'At least one named parent row is required.', PARENT)

    def required(member, number, row, fields, *, always=False):
        for field in fields:
            if (always or operation == 'create' or field in row) and not row.get(field, '').strip():
                state = 'blank' if field in row else 'omitted'
                issue('UNRESOLVED_REQUIRED_INPUT', f'Required {field} is {state}; materialize an evidence-backed default or obtain explicit business input. No default was inferred.', member, number, field)

    parents, children = {}, set()
    for member, rows in tables.items():
        keys = set()
        for number, row in rows:
            required(member, number, row, ('Name',) if member == PARENT else (LINK,), always=True)
            if member == PARENT:
                required(member, number, row, PARENT_REQUIRED)
                key = (row.get('Name'),)
                parents[row.get('Name')] = row
            elif member == CHILD:
                required(member, number, row, ('PlannedForCode',), always=True)
                required(member, number, row, CHILD_REQUIRED)
                for field in AMOUNT_FIELDS:
                    if field not in row:
                        if operation != 'create' or field not in CHILD_REQUIRED:
                            issue('AMOUNT_TUPLE_OMITTED', 'Importer dereferences all ten amount-set elements even on update. Materialize this field from an authorized retained baseline or explicit create input; omission is not proven preservation.', member, number, field)
                key = (row.get(LINK), row.get('PlannedForCode'))
                children.add(key)
            else:
                identity = {
                    CURRENCY: ('PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode', 'TxnCurrencyCode'),
                    'ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv': ('SetCode',),
                    'PJO_PPT_PLAN_OPTION_RATE_SCH.csv': ('ShortCode',),
                    'PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv': ('Language',),
                }[member]
                required(member, number, row, identity, always=True)
                if member == 'PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv':
                    required(member, number, row, ('Name', 'SourceLang'), always=True)
                key = tuple(row.get(f) for f in (LINK, *identity))
            if key in keys:
                issue('DUPLICATE_IDENTITY', 'Multiple rows address the same task identity.', member, number)
            keys.add(key)
            parsed_dates = {}
            for field, value in row.items():
                if not value:
                    continue
                domain = {'Y', 'N'} if field in YES_NO else DOMAINS.get(field)
                if domain is not None and value not in domain:
                    issue('NONCANONICAL_VALUE', 'Serialize one canonical code from '+', '.join(sorted(domain))+'. Resolve business wording before packaging.', member, number, field)
                if field in {'StartDate', 'EndDate', 'NtpRateDate', 'PcCostRateDate', 'PcRevRateDate', 'PfcCostRateDate', 'PfcRevRateDate', 'RateSchCostRateDate', 'RateSchRevRateDate'}:
                    # The target FSM export uses YYYY/MM/DD; retain ISO support.
                    # Parse for validation only, without rewriting approved bytes.
                    if re.fullmatch(r'\d{4}([/-])\d{2}\1\d{2}', value):
                        try:
                            parsed_dates[field] = date.fromisoformat(value.replace('/', '-'))
                        except ValueError:
                            issue('INVALID_DATE', 'Supplied calendar date does not exist.', member, number, field)
                    else:
                        issue('UNRESOLVED_DATE_FORMAT', 'Date must use YYYY/MM/DD or YYYY-MM-DD. Resolve against the target CSV date contract before approval; no locale or timestamp conversion was inferred.', member, number, field)
            if member == PARENT and all(f in parsed_dates for f in ('StartDate', 'EndDate')):
                if parsed_dates['EndDate'] < parsed_dates['StartDate']:
                    issue('DATE_ORDER', 'EndDate must not precede StartDate.', member, number, 'EndDate')

    for member, rows in tables.items():
        for number, row in rows:
            if member != PARENT and row.get(LINK) not in parents:
                issue('PARENT_LINK', 'Child does not reference a parent in this package.', member, number, LINK)
            if member == CURRENCY and (row.get(LINK), row.get('PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode')) not in children:
                issue('PLANNING_ROW_LINK', 'Currency row does not reference a planning-options row in this package.', member, number)
            if member == RATES:
                schedules = tuple(f for f in row if (f.startswith('RateScheduleName') or f == 'IndSchName') and row[f].strip())
                if schedules:
                    required(member, number, row, ('UsePlanningRatesFlag',), always=True)
                # Row mode is independent of the general planning-option flag.
                # Inactive retained values are not evidence of a requested change.
                planning_only = {'RateScheduleName2', 'RateScheduleName3', 'RateScheduleName4',
                                 'RateScheduleName5', 'RateScheduleName6', 'RateScheduleName7', 'IndSchName'}
                if row.get('UsePlanningRatesFlag') == 'N' and any(f in planning_only for f in schedules):
                    result['deferredChecks'].append({'code': 'INACTIVE_RATE_SCHEDULES', 'status': 'deferred', 'member': member, 'row': number, 'message': 'Person, job, nonlabor and burden schedules are inactive in actual-rate mode. Retained values may remain; the assisted rules must reject requested changes to inactive controls without clearing retained data.'})
            if member != CHILD:
                continue
            parent = parents.get(row.get(LINK), {})
            if row.get('AmountSetTypeCode') and row.get('PlannedForCode') and row['AmountSetTypeCode'] != row['PlannedForCode']:
                result['deferredChecks'].append({'code': 'AMOUNT_SET_COMPATIBILITY', 'status': 'deferred', 'member': member, 'row': number, 'attribute': 'AmountSetTypeCode', 'message': 'Explicit amount-set type retained. UI default equals planning scope, but importer accepts supplied type and no equality invariant or complete type domain was established.'})
            if row.get('AutoBdgtBaseline') == 'Y':
                result['deferredChecks'].append({'code': 'BASELINE_CONTROL_CONTEXT', 'status': 'deferred', 'member': member, 'row': number, 'message': 'Verify budgetary-control eligibility. UI bcFlag/TransBdgtCtrlFlag disable this choice; direct equivalence to parent CSV BudgetaryControlsFlag is not established.'})
                if row.get('GenBdgtDuringBaseline') != 'Y':
                    issue('BASELINE_GENERATION_REQUIRED', 'Automatic budget baseline requires explicit GenBdgtDuringBaseline=Y (retain from baseline for update).', member, number, 'GenBdgtDuringBaseline')
            if row.get('AutoBdgtBaseline') == 'Y' or row.get('GenBdgtDuringBaseline') == 'Y':
                required(member, number, row, ('Name2',), always=True)
            if row.get('ProgAutoGenFcstVer') == 'Y':
                required(member, number, row, ('Name3',), always=True)
            if row.get('PlanInMultiCurrFlag') and parent.get('PlanInMultiCurrFlag') and row['PlanInMultiCurrFlag'] != parent['PlanInMultiCurrFlag']:
                issue('PARENT_CHILD_MISMATCH', 'Importer synchronizes child multiple-currency choice from its parent; supply matching retained choices.', member, number, 'PlanInMultiCurrFlag')
            permitted = {'COST_ONLY': {'COST'}, 'REVENUE_ONLY': {'REVENUE'}, 'COST_AND_REV_TOGETHER': {'COST_AND_REV_TOGETHER'}, 'COST_AND_REV_SEP': {'COST', 'REVENUE'}}.get(parent.get('PlanOptionCode'))
            if permitted and row.get('PlannedForCode') not in permitted:
                issue('PLANNING_CONTEXT', 'Child planning scope is incompatible with parent PlanOptionCode.', member, number, 'PlannedForCode')
            if row.get('NtpRateDateType'):
                branch = 'BUDGET' if row.get('PlannedForCode') == 'REVENUE' else 'PRJ_PLAN'
                dates = {'EFFECTIVE_RATE_DATE', 'FIXED_DATE', 'SYSTEM_DATE', 'START_DATE_'+branch, 'END_DATE_'+branch}
                if row['NtpRateDateType'] not in dates:
                    issue('NONCANONICAL_VALUE', 'Rate derivation code is incompatible with child scope.', member, number, 'NtpRateDateType')
                required(member, number, row, ('TimePhasedCode',), always=True)
                if row.get('TimePhasedCode') in {'G', 'P'} and row['NtpRateDateType'] not in {'EFFECTIVE_RATE_DATE', 'START_DATE_'+branch}:
                    issue('CALENDAR_RATE_DATE', 'Periodic planning permits only start-of-line or effective resource rate dates; fixed, system and finish dates require calendar None.', member, number, 'NtpRateDateType')
            if row.get('Name', '').strip():
                required(member, number, row, ('TimePhasedCode',), always=True)
                if row.get('TimePhasedCode') == 'N':
                    issue('PERIOD_PROFILE_CONTEXT', 'A period profile is inactive with calendar None. Resolve the requested calendar/profile together before packaging.', member, number, 'Name')
            for prefix in ('Ntp', *CONVERSION_PREFIXES):
                # Disabled project-level override controls retain their values;
                # they do not activate a new fixed-date input requirement.
                control = 'Spec'+prefix+'AtProjLevel'
                if operation == 'update' and prefix in ('PcCost', 'PcRev', 'PfcCost', 'PfcRev') and row.get(prefix+'RateDateType') == 'FIXED_DATE' and not row.get(control):
                    issue('UNRESOLVED_CONDITIONAL_CONTEXT', 'Retain the project-level override choice to establish whether this fixed-date requirement is enabled.', member, number, control)
                    continue
                enabled = row.get(control) != 'N'
                if enabled and row.get(prefix+'RateDateType') == 'FIXED_DATE':
                    required(member, number, row, (prefix+'RateDate',), always=True)
            if row.get('SyncTaskTxnPlanDates') == 'Y':
                if not row.get('SyncTxnDateBuffer'):
                    issue('UNMATERIALIZED_DEFAULT', 'Synchronization is enabled: preparation must materialize the 0-day save default when the effective buffer is empty. No additional business input is required.', member, number, 'SyncTxnDateBuffer')
                elif not re.fullmatch(r'-?[0-9]+', row['SyncTxnDateBuffer']):
                    issue('INVALID_INTEGER', 'A supplied active date buffer must be an integer; an empty input defaults to 0 during preparation.', member, number, 'SyncTxnDateBuffer')
            if row.get('PercentCompCalcMethod') == 'COST' and row.get('EnableCostsForProjPlan') == 'N':
                issue('INCOMPATIBLE_CHOICE', 'Cost percent complete requires costs enabled.', member, number, 'PercentCompCalcMethod')
            if row.get('PercentCompRollupMethod') == 'COST' and row.get('EnableCostsForProjPlan') == row.get('EnableRevForProjPlan') == 'N':
                result['deferredChecks'].append({'code': 'INACTIVE_COST_ROLLUP', 'status': 'deferred', 'member': member, 'row': number, 'attribute': 'PercentCompRollupMethod', 'message': 'The UI retains a disabled COST create default with costs off. Preserve retained/default state; the assisted rules must reject an explicit request to activate cost rollup without costs or revenue.'})
    if operation == 'create':
        for name in parents:
            if not any(key[0] == name for key in children):
                issue('MISSING_PLANNING_ROW', 'Create requires an explicit planning-options child row.', CHILD, attribute=LINK)
    return finish()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--operation', choices=('create', 'update'), required=True)
    args = parser.parse_args()
    outcome = validate_archive(args.archive.read_bytes(), operation=args.operation)
    print(json.dumps(outcome, indent=2))
    raise SystemExit(0 if outcome['taskContractValidation']['status'] == 'passed' else 1)
