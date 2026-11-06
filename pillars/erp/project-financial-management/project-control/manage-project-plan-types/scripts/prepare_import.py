#!/usr/bin/env python3
"""Prepare one named plan type from a current target template and data baseline.

Inputs use already-resolved CSV attributes. This helper never resolves LOVs,
approves, uploads or calls Fusion. Create defaults cover PROJECT_PLAN/BUDGET/
COST_ONLY only. Updates merge exact retained rows without create defaults.
Submitted synchronized options with an empty buffer receive the save default 0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import stat
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import zipfile

from validate_import import (COLUMNS, PARENT, CHILD, CURRENCY, LINK, META, TASK,
                             validate_archive, shared_conversion_intent, validate_source_intent)

# Explicit values from ora_defaulting_rules.md; never derive defaults from
# column spelling, required-field lists, row frequency or another record.
PARENT_DEFAULTS = dict(PlanTypeCode='PROJECT_PLAN', PlanClassCode='BUDGET',
    PlanOptionCode='COST_ONLY', PlanInMultiCurrFlag='N', EnableWfFlag='N',
    DefaultFinPlanTypeFlag='N', AutoApproveFlag='N', DefaultAwdFinPlanTypeFlag='N')
CHILD_DEFAULTS = dict(PlanOptionLevelCode='PLAN_TYPE', ObjectTypeCode='PROJECT',
    PlannedForCode='COST', PlanTypeCode='PROJECT_PLAN', PlanInMultiCurrFlag='N',
    AllowFcstAmtCarryFlag='N', FactorByCode='1', SpecPcRevAtProjLevel='N',
    SpecPfcRevAtProjLevel='N', SpecPcCostAtProjLevel='N', SpecPfcCostAtProjLevel='N',
    SyncTaskTxnPlanDates='N', GenBdgtDuringBaseline='N', AutoBdgtBaseline='N',
    UseThirdPartySoftware='N', AutoRollupTaskDate='N', RaTaskDatesSame='N',
    UsePlanningRatesFlag='N', EnableCostsForProjPlan='N', AllowNegEtcFlag='N',
    ProgAutoApprFcstVer='N', ProgAutoGenFcstVer='N', ProgUpdPlanQtyWithEac='N',
    AmountSetTypeCode='COST', RawCostFlag='Y', CostQtyFlag='Y', BrdndCostFlag='Y',
    RevenueFlag='N', RevenueQtyFlag='N', AllQtyFlag='N', BillRateFlag='N',
    CostRateFlag='Y', BrdndRateFlag='Y', TimePhasedCode='N',
    NtpRateDateType='START_DATE_PRJ_PLAN', PercentCompCalcMethod='MANUAL',
    EtcMethodCode='MANUAL', PercentCompRollupMethod='COST',
    AutoPlanAsmtFlag='N', MapActSummaryFlag='N', ManualSpreadFlag='N')
KEYS = {
    CHILD: ('PlannedForCode',), CURRENCY: ('PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode', 'TxnCurrencyCode'),
    'ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv': ('SetCode',),
    'PJO_PPT_PLAN_OPTION_RATE_SCH.csv': ('ShortCode',),
    'PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv': ('Language',),
}
INSERTABLE = set(KEYS) - {CHILD}
TRANSLATION = 'PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv'


def validate_requested_options(effective: dict, requested: dict, *, operation: str, retained: dict | None = None):
    """Check requested activation, without rewriting disabled retained values.

    A complete FSM row can contain inactive UI initialization. Only an explicit
    create choice or a changed update value is an activation request. The byte
    validator cannot recover that distinction from a CSV alone.
    """
    changed = {key: value for key, value in requested.items()
               if operation == 'create' or value != (retained or {}).get(key)}

    def reject(field, message):
        raise ValueError(f'INACTIVE_OPTION: {CHILD}.{field}: {message}')

    conversion_fields = {prefix+suffix for prefix in ('PcCost','PcRev','PfcCost','PfcRev','RateSchCost','RateSchRev')
                         for suffix in ('RateType','RateDateType','RateDate')}
    currency_switches = {'AsgnResInSingleCurrFlag', 'SpecPcCostAtProjLevel', 'SpecPcRevAtProjLevel',
                         'SpecPfcCostAtProjLevel', 'SpecPfcRevAtProjLevel'}
    if any(field in conversion_fields and (operation != 'create' or value.strip())
           or field in currency_switches and (operation != 'create' or value == 'Y')
           for field,value in changed.items()):
        require_financial_settings(effective, 'Currency Settings')

    if effective.get('UseThirdPartySoftware') == 'Y':
        # PLAN_TYPE setup keeps cost/calendar/progress and cost-enabled rate/
        # currency controls editable; PLAN_VERSION restrictions do not apply.
        disabled = {'EnableRevForProjPlan', 'MapActSummaryFlag',
                    'RaTaskDatesSame', 'AutoRollupTaskDate'}
        for field in sorted(changed.keys() & disabled):
            if operation == 'create' and changed[field] == CHILD_DEFAULTS.get(field, ''):
                continue  # An explicit inactive initialization is not activation.
            reject(field, 'This control is disabled by third-party scheduling; choose an active scheduling context first.')
    if effective.get('EnableRevForProjPlan') == 'Y' and effective.get('EnableCostsForProjPlan') != 'Y':
        if changed.get('EnableRevForProjPlan') == 'Y' or changed.get('EnableCostsForProjPlan') == 'N':
            reject('EnableRevForProjPlan', 'Revenue planning requires costs enabled; never silently enable costs.')
    if 'RevClassificationMethod' in changed and effective.get('EnableRevForProjPlan') != 'Y':
        reject('RevClassificationMethod', 'Select a revenue calculation method only with revenue planning enabled.')
    if changed.get('MapActSummaryFlag') == 'Y' and effective.get('AutoPlanAsmtFlag') == 'Y':
        reject('MapActSummaryFlag', 'Summary-task actual association is disabled when unplanned assignments become planned assignments.')
    if changed.get('AutoPlanAsmtFlag') == 'Y' and effective.get('MapActSummaryFlag') == 'Y':
        reject('AutoPlanAsmtFlag', 'Resolve the retained summary-task actual association choice before enabling automatic planned assignments.')
    if changed.get('ManualSpreadFlag') == 'Y' and effective.get('TimePhasedCode') not in {'G', 'P'}:
        reject('ManualSpreadFlag', 'Manual periodic spread requires an Accounting or Project Accounting calendar.')
    if changed.get('ProgAutoApprFcstVer') == 'Y' and effective.get('ProgAutoGenFcstVer') != 'Y':
        reject('ProgAutoApprFcstVer', 'Automatic forecast approval requires automatic forecast generation.')
    if changed.get('PercentCompRollupMethod') == 'COST' and not any(
        effective.get(field) == 'Y' for field in ('EnableCostsForProjPlan', 'EnableRevForProjPlan')):
        reject('PercentCompRollupMethod', 'Activating cost-based rollup requires cost or revenue planning; the inactive create default may be retained.')


def require_financial_settings(options: dict, label: str):
    if options.get('EnableCostsForProjPlan') == options.get('EnableRevForProjPlan') == 'N':
        raise ValueError('INACTIVE_OPTION: '+label+' are disabled in the effective planning context.')
    if options.get('EnableCostsForProjPlan') != 'Y' and options.get('EnableRevForProjPlan') != 'Y':
        raise ValueError('UNRESOLVED_CONDITIONAL_CONTEXT: Retain the exact planning-options row before changing '+label+'.')


def validate_requested_rates(effective: dict, requested: dict, options: dict, *, operation: str, retained: dict | None = None):
    changed = {key: value for key, value in requested.items()
               if operation == 'create' or value != (retained or {}).get(key)}
    schedules = {key for key, value in changed.items() if (operation != 'create' or value.strip())
                 and (key.startswith('RateScheduleName') or key == 'IndSchName')}
    if not schedules and 'UsePlanningRatesFlag' not in changed and retained:
        return
    require_financial_settings(options, 'Rate Settings')
    planning_only = {'RateScheduleName2', 'RateScheduleName3', 'RateScheduleName4',
                     'RateScheduleName5', 'RateScheduleName6', 'RateScheduleName7', 'IndSchName'}
    if effective.get('UsePlanningRatesFlag') != 'Y' and schedules & planning_only:
        raise ValueError('INACTIVE_OPTION: Person, job, nonlabor and burden schedules require this BU row to use planning rates.')
    bill = {'RateScheduleName1', 'RateScheduleName5', 'RateScheduleName6',
            'RateScheduleName7', 'RateScheduleName9'}
    if schedules & bill and options.get('EnableRevForProjPlan') != 'Y':
        raise ValueError('INACTIVE_OPTION: Bill schedules require revenue planning enabled.')


def read_package(content: bytes):
    headers, rows = {}, {}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        entries = archive.infolist()
        if len(entries) != len({e.filename for e in entries}) or sum(e.file_size for e in entries) > 32*1024*1024:
            raise ValueError('Duplicate members or oversized export.')
        if set(e.filename for e in entries) != set(COLUMNS) | {META}:
            raise ValueError('Current export must contain the six supported members and metadata; review a changed contract.')
        for entry in entries:
            if entry.flag_bits & 1 or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('Encrypted members and links are unsupported.')
        metadata = archive.read(META)
        if b'<!DOCTYPE' in metadata.upper() or b'<!ENTITY' in metadata.upper():
            raise ValueError('Unsafe metadata XML.')
        root = ET.fromstring(metadata)
        values = lambda name: [e.text for e in root.iter() if e.tag.split('}')[-1] == name]
        if values('ObjectShortName') != [TASK] or values('ProcessStatus') != ['COMPLETED']:
            raise ValueError('A completed current export for this exact task is required.')
        environment = values('ProcessEnv')
        if len(environment) != 1 or not environment[0]:
            raise ValueError('Export environment identity is missing.')
        for member in COLUMNS:
            reader = csv.reader(io.StringIO(archive.read(member).decode('utf-8-sig'), newline=''), strict=True)
            header = next(reader, [])
            if len(header) != len(set(header)) or set(header) != set(COLUMNS[member]):
                raise ValueError(f'{member}: current headers differ from the supported contract; review before preparing.')
            headers[member], rows[member] = header, []
            for cells in reader:
                if not cells:
                    continue
                if len(cells) != len(header):
                    raise ValueError(f'{member}: malformed export row.')
                rows[member].append(dict(zip(header, cells)))
    return headers, rows, metadata, environment[0].casefold()


def prepare_archive(template: bytes, baseline: bytes, request: dict, *, target_origin: str):
    if not isinstance(request, dict) or set(request) - {'operation', 'rows', 'insertRows', 'rename', 'duplicateFrom', 'copyChildren', 'copyConversionAttributes', 'sourceInput'}:
        raise ValueError('Request accepts operation, rows, optional insertRows, rename, duplicateFrom, copyChildren, sourceInput and copyConversionAttributes=true.')
    request = dict(request)
    shared_intent = shared_conversion_intent(request.get('sourceInput'))
    if shared_intent is True:
        if 'copyConversionAttributes' in request and request['copyConversionAttributes'] is not True:
            raise ValueError('SOURCE_INTENT_MISMATCH: Requested shared conversion conflicts with the canonical action.')
        request['copyConversionAttributes'] = True
    elif shared_intent is False and request.get('copyConversionAttributes'):
        raise ValueError('SOURCE_INTENT_MISMATCH: Independent conversion intent conflicts with the copy action.')
    if 'copyConversionAttributes' in request and request['copyConversionAttributes'] is not True:
        raise ValueError('copyConversionAttributes is an explicit true action, not a persistent UI checkbox. Supply independent role attributes without this action.')
    operation, supplied = request.get('operation'), request.get('rows')
    if operation not in {'create', 'update'} or not isinstance(supplied, dict) or set(supplied) - set(COLUMNS):
        raise ValueError('Declare create/update and rows keyed by exact CSV member.')
    inserts = request.get('insertRows', {})
    if not isinstance(inserts, dict) or set(inserts) - INSERTABLE or (inserts and operation != 'update'):
        raise ValueError('insertRows accepts only new set, BU-rate, currency or translation rows on an existing parent update.')
    headers, _, metadata, environment = read_package(template)
    _, retained, _, baseline_environment = read_package(baseline)
    if environment != baseline_environment:
        raise ValueError('Template and baseline belong to different environments.')
    target = urlsplit(target_origin)
    if (target.scheme != 'https' or not target.hostname or target.username or target.password
        or target.query or target.fragment or target.path not in {'', '/'}):
        raise ValueError('Use the exact configured HTTPS Fusion origin, without credentials, path or query.')
    if target.hostname.split('.')[0].casefold() != environment:
        raise ValueError('Export environment does not match the selected target origin.')
    for member, values in list(supplied.items()) + list(inserts.items()):
        if not isinstance(values, list) or any(not isinstance(row, dict) or set(row)-set(headers[member])
            or any(not isinstance(value, str) for value in row.values()) for row in values):
            raise ValueError(f'{member}: use canonical string attributes from the current template.')
        if member in KEYS:
            identities = [tuple(row[key] for key in KEYS[member]) for row in values
                          if all(row.get(key, '').strip() for key in KEYS[member])]
            if len(identities) != len(set(identities)):
                raise ValueError(f'{member}: INSERT_IDENTITY_EXISTS: duplicate requested child identities are invalid.')
    if len(supplied.get(PARENT, [])) != 1:
        raise ValueError('Exactly one named parent request is required.')
    parent = supplied[PARENT][0]
    name = parent.get('Name', '').strip()
    if not name or name != parent['Name']:
        raise ValueError('Supply a nonblank parent name without surrounding spaces.')
    rename = request.get('rename')
    if 'rename' in request:
        if (operation != 'update' or not isinstance(rename, dict) or set(rename) != {'name', 'languages'}
            or not isinstance(rename['name'], str) or not rename['name'].strip()
            or rename['name'] != rename['name'].strip() or len(rename['name']) > 240
            or not isinstance(rename['languages'], list) or not rename['languages']
            or any(not isinstance(language, str) or not language.strip() for language in rename['languages'])
            or len(set(rename['languages'])) != len(rename['languages'])):
            raise ValueError('Rename requires an update with a distinct name and explicit unique retained languages.')
        if set(supplied) != {PARENT} or set(parent) != {'Name'} or inserts or request.get('copyConversionAttributes'):
            raise ValueError('Prepare rename separately from other changes; reacquire the baseline under its new name before subsequent maintenance.')
        if rename['name'] == name or any(row['Name'].casefold() == rename['name'].casefold()
                                        for row in retained[PARENT] if row['Name'] != name):
            raise ValueError('RENAME_IDENTITY_CONFLICT: The new name must differ and be absent from other retained parents.')
    matches = [row for row in retained[PARENT] if row['Name'] == name]
    if operation == 'create' and matches or operation == 'update' and len(matches) != 1:
        raise ValueError('Create needs an absent identity; update needs exactly one retained parent.')
    source_name = request.get('duplicateFrom')
    source_parent, source_options = None, None
    copy_members = set()
    if 'duplicateFrom' in request:
        if 'rename' in request:
            raise ValueError('Duplicate and rename are separate identity transitions.')
        if operation != 'create' or not isinstance(source_name, str) or not source_name.strip() or source_name == name:
            raise ValueError('Duplicate requires a create with an exact retained source and a distinct new name.')
        sources = [row for row in retained[PARENT] if row['Name'] == source_name]
        options = [row for row in retained[CHILD] if row[LINK] == source_name and row['PlannedForCode'] == 'COST']
        if len(sources) != 1 or len(options) != 1:
            raise ValueError('DUPLICATE_SOURCE_UNRESOLVED: Retain one source parent and its complete COST options row.')
        source_parent, source_options = sources[0], options[0]
        if source_parent.get('BudgetaryControlsFlag') == 'Y':
            raise ValueError('UNMAPPED_COPY_CONTEXT: Budgetary-control child settings are outside this task CSV contract; do not silently omit them.')
        selected = request.get('copyChildren', sorted(INSERTABLE - {TRANSLATION}))
        if (not isinstance(selected, list) or any(not isinstance(member, str) for member in selected)
            or set(selected) - (INSERTABLE - {TRANSLATION}) or len(selected) != len(set(selected))):
            raise ValueError('copyChildren selects unique set, BU-rate and currency members; translations require explicit new-name rows.')
        copy_members = set(selected)
    elif 'copyChildren' in request:
        raise ValueError('copyChildren requires duplicateFrom.')
    output = {member: [] for member in headers}
    changes = []
    derived = []
    if operation == 'create':
        duplicate_defaults = {'StartDate':'1957/01/01', 'EndDate':'',
                              'DefaultFinPlanTypeFlag':'N', 'DefaultAwdFinPlanTypeFlag':'N'}
        output[PARENT] = [{**(source_parent or PARENT_DEFAULTS),
                           **(duplicate_defaults if source_parent else {}), **parent}]
        if any(output[PARENT][0][k] != v for k, v in {'PlanTypeCode':'PROJECT_PLAN', 'PlanClassCode':'BUDGET', 'PlanOptionCode':'COST_ONLY'}.items()):
            raise ValueError('This create preparer covers PROJECT_PLAN/BUDGET/COST_ONLY; resolve other branches independently.')
        options = supplied.get(CHILD, [{}])
        if len(options) != 1:
            raise ValueError('COST_ONLY create needs one COST planning-options row.')
        if LINK in options[0] and options[0][LINK] != name:
            raise ValueError('A child addresses another parent.')
        child_defaults = {**(source_options or CHILD_DEFAULTS), 'PlanInMultiCurrFlag':output[PARENT][0]['PlanInMultiCurrFlag']}
        if source_options:
            if any(source_parent.get(key) != value for key,value in
                   {'PlanTypeCode':'PROJECT_PLAN','PlanClassCode':'BUDGET','PlanOptionCode':'COST_ONLY'}.items()):
                raise ValueError('Duplicate covers a retained PROJECT_PLAN/BUDGET/COST_ONLY source.')
            for field in ('AsgnResInSingleCurrFlag', 'ManualSpreadFlag', 'MapActSummaryFlag', 'EnableCostsForProjPlan', 'AllowFcstAmtCarryFlag'):
                if not child_defaults.get(field):
                    child_defaults[field] = 'N'
            if not child_defaults.get('NtpRateDateType'):
                child_defaults['NtpRateDateType'] = 'START_DATE_PRJ_PLAN'
        output[CHILD] = [{**child_defaults, **options[0], LINK: name}]
        validate_requested_options(output[CHILD][0], options[0],
            operation='update' if source_options else operation, retained=source_options)
        defaults = ((PARENT,duplicate_defaults,parent),) if source_parent else (
            (PARENT,PARENT_DEFAULTS,parent),(CHILD,child_defaults,options[0]))
        changes = [{'member':member, 'attribute':key, 'value':value, 'source':'duplicate_default' if source_parent else 'scoped_create_default',
                    'path':member+'.'+key, 'before':None, 'after':value,
                    'reason':('Omitted duplicate value materialized from the source-backed duplicate policy; explicit choices preserved.' if source_parent else
                              'Omitted create value materialized from the scoped defaulting matrix; explicit choices preserved.')}
                   for member, matrix, explicit in defaults
                   for key,value in matrix.items() if key not in explicit]
        if source_parent:
            for member in copy_members:
                output[member] = [{**row, LINK:name} for row in retained[member] if row[LINK] == source_name]
            derived.append({'path':'duplicateFrom', 'before':source_name, 'after':name,
                'reason':'Explicit new-identity copy of the retained parent/options and selected child collections; source rows unchanged; translations require explicit new-name intent.'})
            for field,value in child_defaults.items():
                if field != LINK and field not in options[0] and value != source_options.get(field):
                    changes.append({'member':CHILD, 'attribute':field, 'value':value,
                        'source':'duplicate_default', 'path':CHILD+'.'+field,
                        'before':source_options.get(field), 'after':value,
                        'reason':'Documented duplicate fallback for a null source value; no general create-default replay.'})
    else:
        output[PARENT] = [{**matches[0], **parent}]
        if (matches[0].get('PlanInMultiCurrFlag') == 'Y'
            and output[PARENT][0].get('PlanInMultiCurrFlag') == 'N'
            and any(row[LINK] == name for row in retained[CURRENCY])):
            raise ValueError('DESTRUCTIVE_CURRENCY_RESET_EXCLUDED: Disabling multicurrency deletes retained currency rows in Fusion; deletion is excluded from this skill.')
    if rename:
        for language in rename['languages']:
            rows = [row for row in retained[TRANSLATION] if row[LINK] == name and row['Language'] == language]
            if len(rows) != 1 or not rows[0].get('SourceLang', '').strip():
                raise ValueError('RENAME_LANGUAGE_UNRESOLVED: Retain one complete translation row for each selected language; never invent its source language.')
            if any(row[LINK] != name and row['Language'] == language
                   and row['Name'].casefold() == rename['name'].casefold() for row in retained[TRANSLATION]):
                raise ValueError('RENAME_IDENTITY_CONFLICT: The translated name belongs to another type in the selected language.')
            row = {**rows[0], 'Name':rename['name']}
            output[TRANSLATION].append(row)
            derived.append({'member':TRANSLATION, 'attribute':'Name',
                'path':TRANSLATION+'['+language+'].Name', 'before':rows[0]['Name'],
                'after':rename['name'], 'reason':'Explicit language-scoped rename through the writable translation child; parent alternate key and child ID/language identity retained.'})
    for member, patches in supplied.items():
        if member == PARENT or member == CHILD and operation == 'create':
            continue
        for patch in patches:
            if LINK in patch and patch[LINK] != name:
                raise ValueError('A child addresses another parent.')
            patch = {**patch, LINK:name}
            if any(not patch.get(key, '').strip() for key in KEYS[member]):
                raise ValueError(f'{member}: explicit child identity is required.')
            if operation == 'create':
                copied = ([row for row in output[member] if all(row[key] == patch[key] for key in KEYS[member])]
                          if source_parent and member in copy_members else [])
                if len(copied) > 1:
                    raise ValueError('Duplicate source contains ambiguous child identities.')
                if member == 'PJO_PPT_PLAN_OPTION_RATE_SCH.csv' and 'UsePlanningRatesFlag' not in patch and not copied:
                    patch['UsePlanningRatesFlag'] = 'N'
                    changes.append({'member':member, 'attribute':'UsePlanningRatesFlag', 'value':'N', 'source':'new_bu_row_default',
                        'path':member+'.UsePlanningRatesFlag', 'before':None, 'after':'N', 'reason':'Documented default for this explicitly requested new BU row.'})
                if copied:
                    copied[0].update(patch)
                else:
                    output[member].append(patch)
            else:
                candidates = [row for row in retained[member] if row[LINK] == name
                              and all(row[key] == patch[key] for key in KEYS[member])]
                if len(candidates) != 1:
                    raise ValueError(f'{member}: update needs exactly one retained child; adding or removing children is a separate operation.')
                if member == CHILD:
                    validate_requested_options({**candidates[0], **patch}, patch,
                        operation=operation, retained=candidates[0])
                output[member].append({**candidates[0], **patch})
    for member, rows in inserts.items():
        for explicit in rows:
            if LINK in explicit and explicit[LINK] != name:
                raise ValueError('A child addresses another parent.')
            row = {**explicit, LINK: name}
            if any(not row.get(key, '').strip() for key in KEYS[member]):
                raise ValueError(f'{member}: explicit child identity is required.')
            identity = tuple(row[key] for key in KEYS[member])
            if any(old[LINK] == name and tuple(old[key] for key in KEYS[member]) == identity
                   for old in retained[member] + output[member]):
                raise ValueError(f'{member}: INSERT_IDENTITY_EXISTS: use an update for a retained identity; duplicate insert requests are invalid.')
            if member == 'PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv' and any(
                not row.get(field, '').strip() for field in ('Name', 'SourceLang')):
                raise ValueError('UNRESOLVED_REQUIRED_INPUT: A new translation requires explicit Name, Language and SourceLang.')
            if member == 'PJO_PPT_PLAN_OPTION_RATE_SCH.csv' and 'UsePlanningRatesFlag' not in row:
                row['UsePlanningRatesFlag'] = 'N'
                changes.append({'member':member, 'attribute':'UsePlanningRatesFlag', 'value':'N',
                    'source':'new_bu_row_default', 'path':member+'.UsePlanningRatesFlag',
                    'before':None, 'after':'N', 'reason':'Documented default for this explicitly requested new BU row; no parent/options defaults applied.'})
            output[member].append(row)
            derived.append({'member':member, 'path':member+'['+','.join(identity)+']',
                'before':None, 'after':dict(row), 'reason':'Explicit insertion of an absent child identity under the retained parent; omitted children remain unchanged.'})
    if (operation == 'update' and output[PARENT][0].get('PlanInMultiCurrFlag')
        != matches[0].get('PlanInMultiCurrFlag')):
        # The importer propagates the parent choice only to submitted XML
        # children. Materialize the exact retained rows and reflect that choice.
        for old in retained[CHILD]:
            if old[LINK] != name:
                continue
            selected = [row for row in output[CHILD] if row['PlannedForCode'] == old['PlannedForCode']]
            if not selected:
                selected = [dict(old)]
                output[CHILD].append(selected[0])
            explicit = next((row for row in supplied.get(CHILD, []) if row.get('PlannedForCode') == old['PlannedForCode']), {})
            choice=output[PARENT][0]['PlanInMultiCurrFlag']
            if 'PlanInMultiCurrFlag' in explicit and explicit['PlanInMultiCurrFlag'] != choice:
                raise ValueError('PARENT_CHILD_MISMATCH: Explicit child multicurrency choice conflicts with the parent.')
            before=selected[0].get('PlanInMultiCurrFlag')
            selected[0]['PlanInMultiCurrFlag']=choice
            if before != choice:
                derived.append({'member':CHILD,'attribute':'PlanInMultiCurrFlag',
                    'path':CHILD+'.PlanInMultiCurrFlag','before':before,'after':choice,
                    'reason':'Explicit parent multicurrency change propagated to the exact retained options row, matching the task importer.'})
    if output[CURRENCY] and output[PARENT][0].get('PlanInMultiCurrFlag') != 'Y':
        raise ValueError('INACTIVE_OPTION: Requested currency rows require multicurrency enabled.')
    if request.get('copyConversionAttributes'):
        if output[PARENT][0].get('PlanOptionCode') != 'COST_ONLY':
            raise ValueError('Conversion-copy preparation covers the evidenced COST_ONLY project-plan branch.')
        options = [row for row in output[CHILD] if row.get('PlannedForCode') == 'COST']
        if not options and operation == 'update':
            options = [dict(row) for row in retained[CHILD] if row[LINK] == name and row.get('PlannedForCode') == 'COST']
            if len(options) == 1:
                output[CHILD].append(options[0])
        if len(options) != 1:
            raise ValueError('Conversion-copy requires exactly one retained or prepared COST options row.')
        child = options[0]
        if child.get('EnableCostsForProjPlan') != 'Y':
            raise ValueError('INACTIVE_OPTION: Conversion-copy requires cost-enabled Currency Settings in this project-plan branch.')
        explicit = next((row for row in supplied.get(CHILD, []) if row.get('PlannedForCode', 'COST') == 'COST'), {})
        if child.get('PlanOptionLevelCode') != 'PLAN_TYPE' or child.get('PlanTypeCode') != 'PROJECT_PLAN':
            raise ValueError('Conversion-copy requires PROJECT_PLAN at PLAN_TYPE; version-specific copying is not applicable.')
        source = 'Pc' if output[PARENT][0].get('PlanInMultiCurrFlag') == 'Y' else 'Pfc'
        for suffix in ('RateType', 'RateDateType'):
            if not child.get(source+'Cost'+suffix, '').strip():
                raise ValueError('UNRESOLVED_REQUIRED_INPUT: Conversion-copy needs '+source+'Cost'+suffix+'; no conversion type or date basis was inferred.')
        assignments = {}
        for amount in ('Cost', 'Rev'):
            for destination in (('Pfc', 'RateSch') if source == 'Pc' else ('RateSch',)):
                for suffix in ('RateType', 'RateDateType', 'RateDate'):
                    assignments[destination+amount+suffix] = child.get(source+amount+suffix, '')
            if source == 'Pc':
                assignments['SpecPfc'+amount+'AtProjLevel'] = child.get('SpecPc'+amount+'AtProjLevel', '')
        for field, value in assignments.items():
            if field in explicit and explicit[field] != value:
                raise ValueError('CONFLICTING_CONVERSION_ATTRIBUTES: '+field+' differs from the requested shared conversion source.')
            before = child.get(field)
            child[field] = value
            if before != value:
                derived.append({'member':CHILD, 'attribute':field, 'path':CHILD+'.'+field,
                    'before':before, 'after':value,
                    'reason':'Explicit PLAN_TYPE conversion-copy action from '+source+' attributes; source copyPcToPfc; no UI flag serialized.'})
    # A requested currency update needs the exact retained options/amount tuple.
    for currency in output[CURRENCY]:
        scope = currency['PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode']
        if not any(row['PlannedForCode'] == scope for row in output[CHILD]):
            candidates = [row for row in retained[CHILD] if row[LINK] == name and row['PlannedForCode'] == scope]
            if operation != 'update' or len(candidates) != 1:
                raise ValueError('Requested currency needs a corresponding planning-options row.')
            output[CHILD].append(candidates[0])
    options = [row for row in output[CHILD] if row.get('PlannedForCode') == 'COST']
    if not options:
        options = [row for row in retained[CHILD] if row[LINK] == name and row.get('PlannedForCode') == 'COST']
    for patch in supplied.get(CURRENCY, []) + inserts.get(CURRENCY, []):
        retained_currency_parent = source_name if source_parent and CURRENCY in copy_members else name
        old = next((row for row in retained[CURRENCY] if row[LINK] == retained_currency_parent
                    and all(row[key] == patch[key] for key in KEYS[CURRENCY])), {})
        if not old or any(value != old.get(field) for field,value in patch.items() if field != LINK):
            require_financial_settings(options[0] if len(options) == 1 else {}, 'Currency Settings')
    for patch in supplied.get('PJO_PPT_PLAN_OPTION_RATE_SCH.csv', []) + inserts.get('PJO_PPT_PLAN_OPTION_RATE_SCH.csv', []):
        effective = next(row for row in output['PJO_PPT_PLAN_OPTION_RATE_SCH.csv'] if row['ShortCode'] == patch['ShortCode'])
        retained_rate_parent = source_name if source_parent and 'PJO_PPT_PLAN_OPTION_RATE_SCH.csv' in copy_members else name
        old = next((row for row in retained['PJO_PPT_PLAN_OPTION_RATE_SCH.csv']
                    if row[LINK] == retained_rate_parent and row['ShortCode'] == effective['ShortCode']), {})
        validate_requested_rates(effective, patch, options[0] if len(options) == 1 else {},
                                 operation='update' if source_parent and old else operation, retained=old)
    # Match the task UI's save-time null default after explicit choices and
    # retained values have been merged. This is not a general create default:
    # keep nonempty values (including zero/negative overrides), disabled values
    # and omitted options rows unchanged. Invalid nonempty values still fail
    # byte validation rather than being replaced with zero.
    for row in output[CHILD]:
        if row.get('SyncTaskTxnPlanDates') == 'Y' and row.get('SyncTxnDateBuffer', '') == '':
            before = row.get('SyncTxnDateBuffer')
            row['SyncTxnDateBuffer'] = '0'
            changes.append({'member':CHILD, 'attribute':'SyncTxnDateBuffer', 'value':'0',
                'source':'conditional_save_default', 'path':CHILD+'.SyncTxnDateBuffer',
                'before':before, 'after':'0',
                'reason':'Synchronization is enabled and the effective buffer is empty; apply the task save default of 0 days. Explicit and retained nonempty buffers take precedence.'})
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for member, header in headers.items():
            table = io.StringIO(newline='')
            writer = csv.DictWriter(table, fieldnames=header, quoting=csv.QUOTE_ALL, lineterminator='\r\n')
            writer.writeheader()
            writer.writerows(output[member])
            archive.writestr(zipfile.ZipInfo(member), table.getvalue().encode())
        archive.writestr(zipfile.ZipInfo(META), metadata)
    content = stream.getvalue()
    validation = validate_archive(content, operation=operation)
    if validation['taskContractValidation']['status'] != 'passed':
        raise ValueError(json.dumps(validation, ensure_ascii=False))
    validate_source_intent(content, request.get('sourceInput'))
    return content, {'operation':operation, 'name':name, 'exportEnvironment':environment,
        'archiveSha256':hashlib.sha256(content).hexdigest(),
        'rowCounts':{member:len(values) for member,values in output.items()},
        'defaultsApplied':changes, 'derivedChanges':derived,
        'rename':({'from':name, 'to':rename['name'], 'languages':rename['languages']} if rename else None),
        'duplicateFrom':source_name,
        'validation':validation}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('template','baseline','request','output'):
        parser.add_argument('--'+flag, type=Path, required=True)
    parser.add_argument('--target-origin', required=True, help='Exact approved Fusion origin from the active project/environment context.')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        content, result = prepare_archive(args.template.read_bytes(), args.baseline.read_bytes(), json.loads(args.request.read_text()), target_origin=args.target_origin)
        if not args.dry_run:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('xb') as destination:
                destination.write(content)
        print(json.dumps({**result, 'written':not args.dry_run, 'archivePath':str(args.output.resolve())}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError, csv.Error) as error:
        print(str(error))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
