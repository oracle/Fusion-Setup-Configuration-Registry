# Reference Lookups

Before executing any REST lookup below, apply the
[REST version and query compatibility preflight](../../../references/rest-query-compatibility.md)
and the REST request compatibility rule in Lookup Execution Rules. Existing
matching, classification precedence and workflow gates continue to apply.

Accept codes, meanings, names, descriptions, translations and ordinary natural-language phrasing in any language when the evidence and context identify one valid member. Resolve intent to one CSV column first, then resolve its value. Do not require English, exact labels or prior knowledge of a code. Reject zero or multiple plausible matches only when a supported authority was actually checked. An unavailable validation route is unresolved, not a no-match result; never silently replace the user's intent.

Immutable lookup tables below are the runtime authority for their finite seeded System values. Period Profile is configured data: apply the Period Profile Evidence Boundary below before using any snapshot. The retained SB4 tables are historical reference material, not selected-target identity or calendar authority. Template exports establish CSV contracts only. FSM export-based reference validation is not selected for this task; unsupported dynamic references remain unresolved/nonblocking.

## Unresolved Validation Policy

Missing supported REST validation or an unverified eligibility predicate produces REFERENCE_UNRESOLVED with severity Warning and blocking=false. Continue the declared workflow, including preview and normal approval, without a waiver or a request to supply research evidence. List every affected field and skipped check in the preview and final result. This status is not successful membership validation.

Preserve the supplied value in its proven CSV representation, or preserve the existing exported value when unchanged. Do not invent IDs, canonicalize an unverified display name, derive an unknown code from prose, or silently omit a requested value. Ask only for a missing representation or genuinely ambiguous business value needed to build the CSV. Unsupported columns and known incompatible values remain separate input/package errors. Supported REST calls that fail authentication, transport or pagination are operational failures, not missing-REST exceptions. Static immutable tables remain authoritative locally and require no REST.

| Reference or check | CSV scope | Unresolved check | Runtime handling |
|---|---|---|---|
| Period Profile without current selected-target evidence | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name | Historical tables do not establish current selected-target identity or calendar compatibility | Preserve the supplied name with REFERENCE_UNRESOLVED, blocking=false; historical absence or calendar differences alone are not invalid input |
| Forecast Financial Plan Type | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name3 | No supported equivalent setup REST eligibility lookup | Preserve supplied name as unverified; warning, continue |
| Budget Generation Financial Plan Type | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name2 | No supported equivalent setup REST eligibility lookup | Preserve supplied name as unverified; warning, continue |
| Generation Source Financial Plan Type | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name4 | No supported equivalent setup REST lookup | Preserve supplied name in the proven import representation; warning, continue |
| Planning Resource Breakdown Structure | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name1; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.VersionNumber | No supported complete setup REST identity/version lookup | Preserve supplied name/version as unverified where import applicability is established; do not require this hidden selector for ordinary setup |
| Output units feature availability | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompCalcMethod | No supported feature-state REST lookup established | Unknown feature state is warning-only; known disabled remains incompatible; never replace ORA_OUTPUT_UNITS with MANUAL |
| Currency eligibility parity | PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TxnCurrencyCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TransCurrencyName | Documented REST exists, but complete UI membership equivalence is unverified | Validate documented identity and known predicates; disclose remaining eligibility uncertainty without blocking |
| Configured flexfield value set | AttributeCategory and Attribute1 through Attribute30 in the parent and planning-option CSVs | Deployment-specific dynamic value authority not established | Preserve supplied values for identified segments; disclose skipped membership checks, continue; do not invent segment labels |

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_yes_no | A supplied or changed field is one of the scoped Yes or No table columns and its task applicability is established | Local Yes or No table below; PJO_YES_NO, System configuration | Resolve an unambiguous code, meaning, translation or ordinary yes/no intent to one member. Preserve omitted optional and disabled fields; do not activate hidden financial-only controls | The same scoped CSV field = canonical Y or N | Ambiguous intent needs clarification; known nonmember is invalid. Unknown applicability is a separate scope check, not evidence to invent a value. |
| resolve_calendar | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode | Local Calendar Type table below; PJO_TIME_PHASED_TYPE, System configuration | Use the project-plan subset only. Award calendar (A) is excluded. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_rate_derivation | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType | Local Rate Derivation Date Type table below; PJO_PRJ_PLN_RATE_DRV_DATE_TYPE, System configuration | For the project-plan cost/all options branch (child PlannedForCode COST or COST_AND_REV_TOGETHER). Resolve calendar first: G/P permits only START_DATE_PRJ_PLAN or EFFECTIVE_RATE_DATE; N permits all five listed values. Do not use the revenue budget-date set for this branch. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_budget_rate_date | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType | Local Bill Rate Derivation Date Type table below; PJO_BDGT_RATE_DRV_DATE_TYPE, System configuration | Only the revenue-only or separate-revenue planning row (child PlannedForCode REVENUE), budget class, non-time-phased context. Do not union this set with the project-plan cost/all set. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_plan_level | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanLevelCode | Local Planning Level table below; PJO_PLAN_LEVEL_CODE, System configuration | Evaluate the active setup context: classic project-plan cost/combined controls do not expose this choice; revenue branches may. Alternate combined layouts require independent reachability evidence and do not authorize a change by themselves. Never infer an A default. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanLevelCode = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_rev_classification | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevClassificationMethod | Local Revenue Calculation Method table below; PJO_REV_CLASSIFICATION_METHOD, System configuration | Apply when project-plan revenue is enabled. All three members are eligible at PLAN_TYPE; do not apply a PLAN_VERSION planning-rate filter. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevClassificationMethod = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_conversion_date | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateDateType | Local Currency Conversion Date Type table below; System lookup data PJO_RATE_DRV_DATE_TYPE and PJO_PRJ_PLN_RATE_DRV_DATE_TYPE, with project-plan eligibility restriction | Use only this three-member project-plan set; system date, effective resource rate dates and budget/forecast line dates are excluded. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateDateType = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_percent_calc | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompCalcMethod | Local Physical Percent Complete Calculation Method table below; PJF_PERCENT_COMP_METHOD, System configuration | Exclude COST when EnableCostsForProjPlan is N. ORA_OUTPUT_UNITS requires ORA_PJO_TASK_OUTPUT_QUANTITIES when feature state is known. Known disabled is incompatible; unknown state without a supported lookup is REFERENCE_UNRESOLVED, warning-only. Never convert to MANUAL. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompCalcMethod = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_progress_etc | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodCode | Local Estimate-to-Complete Method table below; PJF_ETC_METHOD, System configuration | Use the project-plan progress ETC set, not the financial-plan generation ETC lookup. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodCode = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_percent_rollup | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompRollupMethod | Local Primary Physical Percent Complete Basis table below; PJO_PERCENT_COMP_ROLLUP_METHOD, System configuration | Resolve the supplied basis within the applicable project-plan options row. An explicit request to activate COST requires EnableCostsForProjPlan=Y or EnableRevForProjPlan=Y. The inspected create UI retains COST as a disabled default with costs off; preserve this inactive default or retained value without claiming active cost rollup. Do not reject COST merely because costs=N when revenue=Y. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompRollupMethod = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_plan_class | The scoped field is supplied or changed; PJO_PLAN_TYPE_PROJECT.csv.PlanClassCode | Local Plan Class table below; PJO_PLAN_CLASS, System configuration | The PROJECT_PLAN setup route hides this selector and initializes BUDGET. The task validation requires BUDGET for PROJECT_PLAN; reject other class intent as incompatible. | PJO_PLAN_TYPE_PROJECT.csv.PlanClassCode = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_plan_option | The scoped field is supplied or changed; PJO_PLAN_TYPE_PROJECT.csv.PlanOptionCode | Local Planning Amounts table below; PJO_PLAN_OPTION_CODE, System configuration | COST_ONLY is the established creation default. Other canonical members are not automatically authorized for a new PROJECT_PLAN: require branch/package evidence. Preserve evidenced existing combined/separate structure; do not infer parent code from the enable-revenue checkbox. | PJO_PLAN_TYPE_PROJECT.csv.PlanOptionCode = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_planned_for | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlannedForCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode | Local Planning Amounts Row Scope table below; PJO_PLANNED_FOR_CODE, System configuration | This child domain differs from parent PlanOptionCode. COST_ONLY parent has representative COST row; REVENUE_ONLY has REVENUE; separate has representative COST; combined retains COST_AND_REV_TOGETHER. Additional separate-revenue row cardinality needs current package evidence. Currency parent reference must equal its planning-options parent key. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlannedForCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode = canonical code | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_period_profile | Period Profile supplied or changed | Explicitly supplied current target snapshot, when available, scoped under Period Profile Evidence Boundary; retained SB4 tables are historical examples only | Resolve calendar first. With matching current target evidence, uniquely resolve profile ID, name or evidence-grounded wording within that calendar; normalize case/spacing only for matching and retain canonical output. Calendar N remains incompatible with a supplied profile. Without authoritative evidence, preserve the supplied name and record unresolved compatibility | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name = exact Period Profile Name; never serialize an ID. Record evidence basis and target-validation status separately | Authoritative zero/multiple matches or evidenced target calendar mismatch: request correction. Missing, historical or different-target evidence: REFERENCE_UNRESOLVED warning, blocking=false, not a mismatch. An ID-only or ambiguous request still needs an unambiguous name for CSV; never translate it using another target’s ID |
| resolve_forecast_type | Forecast Financial Plan Type supplied or changed | Task capability policy above; requested forecast type name (no identity authority claimed) | FORECAST and FINANCIAL_PLAN are required when eligibility is known. No equivalent setup REST validation is established; do not substitute project-assigned types | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name3 retains supplied display name; no inferred plan type ID; REFERENCE_UNRESOLVED | Warning REFERENCE_UNRESOLVED, blocking=false; continue with unverified supplied CSV value. Known incompatible or ambiguous input remains an error. |
| resolve_ra_plan_type | Budget Generation Financial Plan Type supplied or changed | Task capability policy above; requested budget type name (no identity authority claimed) | Known type must be eligible FINANCIAL_PLAN/BUDGET at PLAN_TYPE with compatible calendar/budget controls. No equivalent setup REST validation is established | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name2 retains supplied display name; no inferred plan type ID; REFERENCE_UNRESOLVED | Warning REFERENCE_UNRESOLVED, blocking=false; continue with unverified supplied CSV value. Known incompatible or ambiguous input remains an error. |
| resolve_existing_plan_type | Existing record eligibility and package branch reconciliation | Completed current target data export with exact task/environment identity; not a template-only package | Resolve the existing record by branch and identity; preserve unrelated rows. Enumerated values use their dedicated local resolver, never observed-row membership. | Existing-record identity, protected-state and duplicate evidence | Block if current existing-record evidence is absent or ambiguous. |
| resolve_task_level_fsm_route | Before package generation or import | Persisted export receipt, completed ZIP, metadata manifest, declared member headers, and task metadata | Exact task/environment; valid ZIP and declared members; template evidence does not establish dynamic reference values | ProcessId, target contract, row counts, checksum | Resume a recorded ProcessId; invalid or premature artifacts block generation. |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_set | The scoped field is supplied or changed; ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv.SetCode | Documented setIdSetsLOV identity contract; task set authority FND_SETID_SETS_VL has no active-date or business-unit eligibility predicate | /fscmRestApi/resources/11.13.18.05/setIdSetsLOV?onlyData=true&limit=500&fields=SetCode,SetName,Description | SetCode, SetName, Description | Complete ordered SetCode paging once per scope/run, then apply Resolver Evaluation below. Resolve code, name, description or evidence-grounded interpretation to one accessible identity. No active/date filter. Identity validation uses the published API contract; exact implementation/security parity is not asserted or required for this limited result. Check plan-type editability and import authorization separately. | ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv.SetCode = SetCode; never numeric SetId; result eligibility is identity_only | Distinguish missing in the visible collection, ambiguous, inaccessible and incomplete acquisition. A zero match is not proof of global nonexistence or lack of eligibility. |
| resolve_conversion_type | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateType | Documented conversion type lookup backed by GL_DAILY_CONVERSION_TYPES | /fscmRestApi/resources/11.13.18.05/currencyConversionTypesLOV?onlyData=true&limit=500&fields=ConversionTypeId,UserConversionType,Description | ConversionTypeId, UserConversionType, Description | Fetch the complete collection once per run; Resolve code, display name or description uniquely, then exclude canonical User for PLAN_TYPE. Preserve string codes, including numeric-looking codes. No active-date filter is established. | PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateType = ConversionTypeId canonical code | Reject supported-authority no-match, ambiguous or known ineligible values. Missing supported eligibility authority is REFERENCE_UNRESOLVED, warning-only; operational read failures remain errors. |
| resolve_employee_schedule | Planning rates are enabled and the scoped schedule is supplied; bill schedules additionally require a revenue branch; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName2; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName5 | PJF_RATE_SCHEDULES_VL with currency and PJF_SCHEDULE_TYPE membership; BU assignment supplied by resolve_business_unit_rate_set | /fscmRestApi/resources/11.13.18.05/rateSchedules?onlyData=true&limit=500&fields=RateScheduleId,RateScheduleName,ScheduleTypeCode,ProjectRatesSetId,CurrencyCode,Description | RateScheduleId, RateScheduleName, ScheduleTypeCode, ProjectRatesSetId, CurrencyCode, Description | Share one complete header fetch across all five schedule resolvers and every CSV row. Resolve BU then resolve_business_unit_rate_set. Require ScheduleTypeCode EMPLOYEE and ProjectRatesSetId in {assigned SetId, 0}; require an assignment even for common-set schedules. The project rate set is ProjectRatesSetId, never the job set. Resolve one eligible identity and retain canonical name; no header active-date restriction. REST adds reference-set joins and data security: missing/inaccessible candidates remain unresolved under this identity, not proof they do not exist. Do not substitute rateSchedulesLOV without its missing currency/type membership checks. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName2; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName5 = exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally | Reject supported-authority no-match, ambiguous or known ineligible values. Missing supported eligibility authority is REFERENCE_UNRESOLVED, warning-only; operational read failures remain errors. |
| resolve_job_schedule | Planning rates are enabled and the scoped schedule is supplied; bill schedules additionally require a revenue branch; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName3; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName6 | PJF_RATE_SCHEDULES_VL with currency and PJF_SCHEDULE_TYPE membership; BU assignment supplied by resolve_business_unit_rate_set | /fscmRestApi/resources/11.13.18.05/rateSchedules?onlyData=true&limit=500&fields=RateScheduleId,RateScheduleName,ScheduleTypeCode,ProjectRatesSetId,CurrencyCode,Description | RateScheduleId, RateScheduleName, ScheduleTypeCode, ProjectRatesSetId, CurrencyCode, Description | Share one complete header fetch across all five schedule resolvers and every CSV row. Resolve BU then resolve_business_unit_rate_set. Require ScheduleTypeCode JOB and ProjectRatesSetId in {assigned SetId, 0}; require an assignment even for common-set schedules. The project rate set is ProjectRatesSetId, never the job set. Resolve one eligible identity and retain canonical name; no header active-date restriction. REST adds reference-set joins and data security: missing/inaccessible candidates remain unresolved under this identity, not proof they do not exist. Do not substitute rateSchedulesLOV without its missing currency/type membership checks. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName3; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName6 = exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally | Reject supported-authority no-match, ambiguous or known ineligible values. Missing supported eligibility authority is REFERENCE_UNRESOLVED, warning-only; operational read failures remain errors. |
| resolve_role_schedule | The scoped schedule is supplied in its business-unit row; actual-rate mode exposes Project Role Cost Rate on the inspected target, while bill schedules require supported revenue context; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName8; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName9 | PJF_RATE_SCHEDULES_VL with currency and PJF_SCHEDULE_TYPE membership; BU assignment supplied by resolve_business_unit_rate_set | /fscmRestApi/resources/11.13.18.05/rateSchedules?onlyData=true&limit=500&fields=RateScheduleId,RateScheduleName,ScheduleTypeCode,ProjectRatesSetId,CurrencyCode,Description | RateScheduleId, RateScheduleName, ScheduleTypeCode, ProjectRatesSetId, CurrencyCode, Description | Share one complete header fetch across all five schedule resolvers and every CSV row. Resolve BU then resolve_business_unit_rate_set. Require ScheduleTypeCode PROJECT_ROLE and ProjectRatesSetId in {assigned SetId, 0}; require an assignment even for common-set schedules. The project rate set is ProjectRatesSetId, never the job set. Resolve one eligible identity and retain canonical name; no header active-date restriction. REST adds reference-set joins and data security: missing/inaccessible candidates remain unresolved under this identity, not proof they do not exist. Do not substitute rateSchedulesLOV without its missing currency/type membership checks. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName8; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName9 = exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally | Reject supported-authority no-match, ambiguous or known ineligible values. Missing supported eligibility authority is REFERENCE_UNRESOLVED, warning-only; operational read failures remain errors. |
| resolve_burden_schedule | Planning rates are enabled and Burden Schedule is supplied; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.IndSchName | Documented active burden schedule lookup backed by PJF_IND_RATE_SCH_VL and PJF_LOOKUPS type PJF_IND_RATE_SCHEDULE_TYPE membership | /fscmRestApi/resources/11.13.18.05/burdenSchedulesLOV?onlyData=true&finder=ActiveBurdenSchedulesFinder&limit=500&fields=BurdenScheduleId,Name,Description,Type,FromDate,ToDate | BurdenScheduleId, Name, Description, Type, FromDate, ToDate | Fetch the complete active collection once per effective-date/run; Require no project/award-specific override and current active-date eligibility. Confirm type membership. No BU restriction or firm-only restriction is established; do not inherit those from other rate schedules. Use the same effective calendar date as the UI; if required pass confirmed UserDate to the active finder. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.IndSchName = canonical Name; never schedule ID | Reject supported-authority no-match, ambiguous or known ineligible values. Missing supported eligibility authority is REFERENCE_UNRESOLVED, warning-only; operational read failures remain errors. |
| resolve_business_unit | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.ShortCode | Current active BU identity; FUN_ALL_BUSINESS_UNITS_V and FUN_BU_PERF_V share current translated organization-name authority; UI SHORT_CODE equals BU_NAME | /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV?onlyData=true&limit=500&fields=BusinessUnitId,BusinessUnitName,ActiveFlag | BusinessUnitId, BusinessUnitName, ActiveFlag | Query once per distinct resolved BU intent using q=ActiveFlag=true and BusinessUnitName='<resolved name>'. This conjunction returned one matching row in the target probe. Resolve names, translations and contextual wording before querying; broaden or page results if wording is not yet canonical, never treat an exact-query miss as proof of invalid intent. Require one active current identity in the same application language as CSV. Do not apply module/intent security finders from unrelated tasks. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.ShortCode = BusinessUnitName, source-proven SHORT_CODE alias; retain BusinessUnitId for rate-set resolution | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_currency | The scoped field is supplied or changed; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TxnCurrencyCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TransCurrencyName | Documented currencies lookup; UI authority FND_CURRENCIES_VL; exact REST backing implementation parity remains unverified | /fscmRestApi/resources/11.13.18.05/currenciesLOV?onlyData=true&limit=500&fields=CurrencyCode,Name,Description,EnabledFlag,StartDateActive,EndDateActive,CurrencyFlag | CurrencyCode, Name, Description, EnabledFlag, StartDateActive, EndDateActive, CurrencyFlag | Fetch the documented collection once per run. Complete UI eligibility parity remains unresolved/nonblocking; do not claim it is proven by REST identity resolution. Enforce enabled not N and nullable inclusive application-date bounds, without CurrencyFlag narrowing. Reconcile code and name to one member. | PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TxnCurrencyCode = CurrencyCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TransCurrencyName = Name | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_nonlabor_schedule | Planning rates are enabled and the scoped schedule is supplied; bill schedules additionally require a revenue branch; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName4; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName7 | PJF_RATE_SCHEDULES_VL with currency and PJF_SCHEDULE_TYPE membership; BU assignment supplied by resolve_business_unit_rate_set | /fscmRestApi/resources/11.13.18.05/rateSchedules?onlyData=true&limit=500&fields=RateScheduleId,RateScheduleName,ScheduleTypeCode,ProjectRatesSetId,CurrencyCode,Description | RateScheduleId, RateScheduleName, ScheduleTypeCode, ProjectRatesSetId, CurrencyCode, Description | Share one complete header fetch across all five schedule resolvers and every CSV row. Resolve BU then resolve_business_unit_rate_set. Require ScheduleTypeCode NON-LABOR and ProjectRatesSetId in {assigned SetId, 0}; require an assignment even for common-set schedules. The project rate set is ProjectRatesSetId, never the job set. Resolve one eligible identity and retain canonical name; no header active-date restriction. REST adds reference-set joins and data security: missing/inaccessible candidates remain unresolved under this identity, not proof they do not exist. Do not substitute rateSchedulesLOV without its missing currency/type membership checks. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName4; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName7 = exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_resclass_schedule | The scoped schedule is supplied in its business-unit row, including resource-class fallback in actual-rate mode; bill schedules additionally require a revenue branch; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName1 | PJF_RATE_SCHEDULES_VL with currency and PJF_SCHEDULE_TYPE membership; BU assignment supplied by resolve_business_unit_rate_set | /fscmRestApi/resources/11.13.18.05/rateSchedules?onlyData=true&limit=500&fields=RateScheduleId,RateScheduleName,ScheduleTypeCode,ProjectRatesSetId,CurrencyCode,Description | RateScheduleId, RateScheduleName, ScheduleTypeCode, ProjectRatesSetId, CurrencyCode, Description | Share one complete header fetch across all five schedule resolvers and every CSV row. Resolve BU then resolve_business_unit_rate_set. Require ScheduleTypeCode RESOURCE_CLASS and ProjectRatesSetId in {assigned SetId, 0}; require an assignment even for common-set schedules. The project rate set is ProjectRatesSetId, never the job set. Resolve one eligible identity and retain canonical name; no header active-date restriction. REST adds reference-set joins and data security: missing/inaccessible candidates remain unresolved under this identity, not proof they do not exist. Do not substitute rateSchedulesLOV without its missing currency/type membership checks. | PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName1 = exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally | Reject invalid, ambiguous or known ineligible values. Apply Unresolved Validation Policy to unsupported dynamic authority or feature checks; do not treat missing REST as no match or invent required values. |
| resolve_business_unit_rate_set | A rate schedule is supplied, after resolve_business_unit | Documented BU reference-set assignment lookup; target finder verifies BU, PJF_RATES and selected determinant; REST implementation source unavailable | /fscmRestApi/resources/11.13.18.05/setIdAssignmentsBusinessUnitLOV?onlyData=true&limit=500&finder=AssignmentFinder;DeterminantValue=<BusinessUnitId>,ReferenceGroupName=PJF_RATES&fields=DeterminantType,DeterminantValue,ReferenceGroupName,SetId,SetCode | DeterminantType, DeterminantValue, ReferenceGroupName, SetId, SetCode | Query once per distinct selected BU and reuse within this run. Require exactly one assignment, DeterminantType BU, matching selected BusinessUnitId and ReferenceGroupName PJF_RATES. Authority is documented semantics plus live field verification; do not describe its unavailable implementation as code-proven. | Internal assigned SetId for schedule eligibility; no direct CSV output | Block missing, duplicate, mismatched or incomplete assignment evidence. |

## Lookup Execution Rules

Resolve Use planning rates per PJO_PPT_PLAN_OPTION_RATE_SCH.csv business-unit
row. N uses actual rates and permits applicable fallback schedules: Resource
Class Raw Cost Rate and, on the inspected target, Project Role Cost Rate. Y
exposes Person, Job, Nonlabor Resource, Project Role, Resource Class and Burden
Schedule. Bill controls additionally need revenue context. The resource-class
and role resolvers must still validate every requested fallback schedule using
the same BU/rates-set/type authority. Do not require Y just to use these
fallbacks, or substitute the general-options UsePlanningRatesFlag for the BU
row's choice. Preserve inactive retained schedule values, but do not accept a
requested change to an inactive control as applied.

| Situation | What Happens |
|---|---|
| REST request compatibility | Before a workflow-selected request, determine framework applicability and the effective REST framework version from the selected core client or workflow. Use compatible query syntax and verify that the outgoing header agrees; never pin an independent pillar version. Apply the linked offering preflight, preserve finder separators and literal values, and stop the affected request on an unresolved version or header/query conflict. |
| Shared financial-only static domain | Use its table for contextual reference only. A shared CSV column does not establish PROJECT_PLAN applicability. Never union alternate code sets or make hidden fields mandatory. |
| UI-only Budgetary Control choice | Resolve membership from the local table and applicable context. A missing CSV mapping blocks that requested change; disclose it as unsupported and not applied. Continue independent supported work without claiming the whole request complete. |
| Static field supplied | Resolve locally from its complete canonical table and applicable branch. Do not call REST, export or a database to validate that static field. |
| Dynamic field supplied | Use only the active workflow-selected read-only adapter or an explicitly supplied current target snapshot with the documented attributes. Use the verified requests and remaining parity gates below; live probes were read-only on 2026-09-12. A successful response does not prove unavailable backing-source predicates. |
| A current snapshot has no selected acquisition route | Record REFERENCE_UNRESOLVED and the skipped check; continue with the proven supplied representation. Do not substitute an undeclared acquisition route. |
| A paginated lookup is used | Request limit=500 explicitly; follow hasMore with offset advanced by the returned item count until false. Empty/non-progressing or failed later pages block completeness. Cache only within the same run, environment, identity, language, effective date and query scope. Observed counts are planning evidence, never hardcoded valid values or permanent size limits. |
| Small collection strategy | Fetch currencies, reference sets, conversion types, active burden schedules and shared rate schedule headers once per scope/run; reuse across CSV rows. Complete all pages; never silently cap at 500. |
| Large BU and assignment collections | Query each distinct BU intent and its PJF_RATES assignment, with limit=500. Reuse results within the run. Follow all relevant pages before no-match/ambiguity decisions. |
| Schedule query optimization | Share a complete compact rateSchedules header fetch across schedule types. Bare RateScheduleName equality returned HTTP 400 on both schedule resources; do not publish it as verified. PersonScheduleTypeFinder is capped at one row. Use the shared complete fetch; future selective expressions require a target probe. |
| Source parity remains incomplete | Disclose currency eligibility parity as unresolved/nonblocking. Reference-set identity validation is supported by the documented API and the task's unfiltered set-membership contract; do not claim REST/UI security equivalence, editability or import privilege. BU-rate assignment semantics remain documented and live-tested, not code-proven. |
| No supported acquisition route exists | Apply Unresolved Validation Policy to profiles without current selected-target evidence, forecast type, budget-generation target, RBS Name1/VersionNumber and generation-source Name4. These gaps do not block the request; never substitute assigned project values for a complete setup catalog |
| Local resolver results are evaluated | Evaluate only applicable static tables and supplied current snapshots. If all supported checks pass, proceed to design enforcement while carrying any nonblocking unresolved warnings. Enter LIVE_LOVS when an applicable Live Lookups acquisition is required and its declared adapter prerequisites are ready. |
| A live resolver result is evaluated | Execute only required Live Lookups rows, then evaluate their dependent snapshot resolvers. Do not rerun static resolvers externally. Require supported checks to finish before design enforcement; carry unresolved/nonblocking checks forward without marking them validated. |
| NtpRateDateType supplied | Resolve PlannedForCode/row context first. Project-plan cost/all and revenue budget branches use separate tables; never union their permitted codes. |
| A hidden or non-exported option is requested | Use the mismatch gates in input validation. A UI control without a CSV mapping cannot be serialized by inventing a column. |

## Period Profile Evidence Boundary

Period profiles are configured per environment. Use a snapshot for identity or a blocking calendar decision only when its source identifies the selected configured target, its acquisition timestamp is current for this run, and its coverage and calendar attributes support the requested match. A short environment alias, a matching historical name/ID, or the historical SB4 observation date alone does not establish this binding. Apply the existing Scope and freshness contract; never reuse another target’s evidence.

No new lookup, required customer evidence, or workflow step is introduced. When matching current evidence is unavailable, keep an unambiguous supplied profile name unchanged, disclose REFERENCE_UNRESOLVED with blocking=false, and continue the supported package/preview workflow. Do not ask for research evidence or invent an acquisition route. Historical tables alone must not canonicalize a target identity, reject a calendar choice, or establish current membership. Calendar N with a supplied profile remains the existing input incompatibility regardless of evidence.

## Period Profile — Accounting Calendar
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name

| Period Profile ID | Period Profile Name |
|---|---|
| 1 | Accounting Period |
| 100000015522630 | Budget Alternative  Profile |
| 10040 | Budget Profile |
| 10041 | Forecast Profile |
| 10042 | Quarterly |

Historical calendar context: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode = G. Source: user-selected snapshot of database view PJO_PERIOD_PROFILES_VL on SB4, read 2026-09-17. Retained for source traceability only; apply Period Profile Evidence Boundary before any target resolution. No runtime database, REST or export is introduced. CSV still contains a name, not an ID.

## Period Profile — Project Accounting Calendar
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name

| Period Profile ID | Period Profile Name |
|---|---|
| 10043 | Fortnightly |
| 2 | Project Accounting Period |

Historical calendar context: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode = P. Source: user-selected snapshot of database view PJO_PERIOD_PROFILES_VL on SB4, read 2026-09-17. Retained for source traceability only; apply Period Profile Evidence Boundary before any target resolution. No runtime database, REST or export is introduced. CSV still contains a name, not an ID.

The historical name Budget Alternative  Profile contains two spaces between Alternative and Profile. Preserve the supplied name unless current selected-target evidence establishes a canonical spelling. Historical spelling and table absence do not override the unresolved/nonblocking policy.

## Resolver Evaluation

For BU acquisition, retain all page responses and the effective request scope
in the input contract described in `scripts/README.md`. Run the offline
`scripts/reference_evidence.py` checker before reporting a match or no-match.
It rejects incomplete pagination, duplicate identities and a version-1 header
combined with an expanded cross-attribute AND query. Headers/default-version
evidence must come from the selected workflow preflight; this checker neither
selects a version nor authorizes acquisition. A partial broad-search page is
not an exhaustive alternatives list. If a fresh task export references the
requested BU but the lookup returns zero, reconcile query compatibility,
identity visibility and active status before suggesting a replacement; the
export references alone do not establish current eligibility.

These are executable assisted resolver instructions owned by this file's Task
Nodes; no new Python runner or resource-local processor is required.

| Stage | Required Contract |
|---|---|
| Select acquisition | At RESOLVE_LOVS, select LIVE_LOVS only for an applicable declared runtime REST read whose prerequisites are ready. Period-profile resolution follows Period Profile Evidence Boundary; absent current selected-target evidence produces a nonblocking warning and cannot select a nonexistent acquisition route |
| Acquire sets | Use core.fusion-api.rest-api-client, its standard Fusion GET client and declared OAuth route. Confirm target configuration, authenticated identity and application language. Use the declared endpoint with orderBy=SetCode, offset=0, onlyData=true and limit=500. Validate count, offset, items and Boolean hasMore. Advance offset by actual returned count until hasMore=false. Empty/non-progressing hasMore=true, repeated SetCode, missing SetCode/SetName, malformed or failed later pages are REFERENCE_INCOMPLETE or REFERENCE_INACCESSIBLE. Do not hardcode observed counts. |
| Scope and freshness | Scope each result to environment, read identity, application language and this run ID; retain acquisition timestamp and completed-page evidence. Reject stale, cross-target or mismatched evidence with REFERENCE_CONTEXT. No cross-run cache. A prior successful request never proves present access. |
| Interpret intent | Against the complete authority, match supplied code, name or description. Normalize case and whitespace for candidate discovery without changing canonical output. Accept translations and contextual wording when evidence establishes the interpretation; record the candidate identities and reason. Never pick a fuzzy first match. If interpretation remains uncertain, ask for the missing disambiguator instead of rejecting non-English input. |
| Set identity | Zero candidates: REFERENCE_MISSING within the visible authorized collection only. Multiple distinct SetCode candidates: REFERENCE_AMBIGUOUS. Exactly one: emit its canonical SetCode and identity_only result. Do not use a numeric SetId in the CSV. |
| Profile identity and compatibility | Apply resolve_period_profile and Period Profile Evidence Boundary. Only current selected-target evidence can establish a profile identity or blocking calendar mismatch; otherwise preserve the supplied name with unresolved/nonblocking status. Historical tables alone never prove a mismatch. Calendar N remains incompatible with a supplied profile |
| Limited claims | Record accessible set identity only. It proves neither plan-type editability, import privilege, BU assignment nor REST/UI security equivalence. Remaining supported dependency, design and package checks must pass before preview; unresolved warnings must remain visible |
| Diagnostic handoff | Attach the resolver, scoped field, environment, stage, result code, classified failure and next action to the invoking node outcome. Preserve known asynchronous request IDs. Persist sanitized audit facts, never credentials or customer reference rows. Missing/ambiguous/incompatible values are input-validation failures; inaccessible reads are auth/authz or transport failures as evidenced; operationally incomplete sources remain failures. An unsupported validation contract is REFERENCE_UNRESOLVED with blocking=false, not an input failure. |

The [published set-ID sets API contract](https://docs.oracle.com/en/cloud/saas/applications-common/26b/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-setidsetslov-get.html)
defines the identity fields and paging used here. The 26C counterpart was not
available during verification; no newer behavior is inferred.

## Calendar Type
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode

| Lookup Code | Meaning |
|---|---|
| G | Accounting calendar |
| N | None |
| P | Project accounting calendar |

Authority: PJO_TIME_PHASED_TYPE, System configuration. Use the project-plan subset only. Award calendar (A) is excluded. Resolve to canonical code.

## Rate Derivation Date Type
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType

| Lookup Code | Meaning |
|---|---|
| EFFECTIVE_RATE_DATE | Effective resource rate dates |
| END_DATE_PRJ_PLAN | Finish date of project plan line |
| FIXED_DATE | Fixed date |
| START_DATE_PRJ_PLAN | Start date of project plan line |
| SYSTEM_DATE | System date |

Authority: PJO_PRJ_PLN_RATE_DRV_DATE_TYPE, System configuration. For the project-plan cost/all options branch (child PlannedForCode COST or COST_AND_REV_TOGETHER). Resolve calendar first: G/P permits only START_DATE_PRJ_PLAN or EFFECTIVE_RATE_DATE; N permits all five listed values. Do not use the revenue budget-date set for this branch. Resolve to canonical code.

## Bill Rate Derivation Date Type
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType

| Lookup Code | Meaning |
|---|---|
| EFFECTIVE_RATE_DATE | Effective resource rate dates |
| END_DATE_BUDGET | To date of budget line |
| FIXED_DATE | Fixed date |
| START_DATE_BUDGET | From date of budget line |
| SYSTEM_DATE | System date |

Authority: PJO_BDGT_RATE_DRV_DATE_TYPE, System configuration. Only the revenue-only or separate-revenue planning row (child PlannedForCode REVENUE), budget class, non-time-phased context. Do not union this set with the project-plan cost/all set. Resolve to canonical code.

## Planning Level
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanLevelCode

| Lookup Code | Meaning |
|---|---|
| A | Project and all tasks |
| P | Project |
| T | Project and top tasks |

Authority: PJO_PLAN_LEVEL_CODE, System configuration. Evaluate the active setup context: classic project-plan cost/combined controls do not expose this choice; revenue branches may. Alternate combined layouts require independent reachability evidence and do not authorize a change by themselves. Never infer an A default. Resolve to canonical code.

## Revenue Calculation Method
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevClassificationMethod

| Lookup Code | Meaning |
|---|---|
| CONTRACT | Contract revenue classification method |
| MANUAL | Manual entry |
| RATE_BASED | Planning rate based |

Authority: PJO_REV_CLASSIFICATION_METHOD, System configuration. Apply when project-plan revenue is enabled. All three members are eligible at PLAN_TYPE; do not apply a PLAN_VERSION planning-rate filter. Resolve to canonical code.

## Currency Conversion Date Type
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateDateType

| Lookup Code | Meaning |
|---|---|
| FIXED_DATE | Fixed date |
| END_DATE_PRJ_PLAN | Finish date of project plan line |
| START_DATE_PRJ_PLAN | Start date of project plan line |

Authority: System lookup data PJO_RATE_DRV_DATE_TYPE and PJO_PRJ_PLN_RATE_DRV_DATE_TYPE, with project-plan eligibility restriction. Use only this three-member project-plan set; system date, effective resource rate dates and budget/forecast line dates are excluded. Resolve to canonical code.

## Physical Percent Complete Calculation Method
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompCalcMethod

| Lookup Code | Meaning |
|---|---|
| COST | Cost |
| EFFORT | Effort |
| MANUAL | Manual entry |
| ORA_OUTPUT_UNITS | Output units |

Authority: PJF_PERCENT_COMP_METHOD, System configuration. Exclude COST when EnableCostsForProjPlan is N. ORA_OUTPUT_UNITS requires ORA_PJO_TASK_OUTPUT_QUANTITIES when feature state is known. Known disabled is incompatible; unknown state without a supported lookup is REFERENCE_UNRESOLVED, warning-only. Never convert to MANUAL. Resolve to canonical code.

## Estimate-to-Complete Method
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodCode

| Lookup Code | Meaning |
|---|---|
| MANUAL | Manual entry |
| REMAINING_PLAN | Remaining plan |

Authority: PJF_ETC_METHOD, System configuration. Use the project-plan progress ETC set, not the financial-plan generation ETC lookup. Resolve to canonical code.

## Primary Physical Percent Complete Basis
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompRollupMethod

| Lookup Code | Meaning |
|---|---|
| COST | Cost |
| EFFORT | Effort |
| MANUAL | Manual entry |

Authority: PJO_PERCENT_COMP_ROLLUP_METHOD, System configuration. Resolve the supplied basis within the applicable project-plan options row. An explicit request to activate COST requires EnableCostsForProjPlan=Y or EnableRevForProjPlan=Y. The inspected create UI retains COST as a disabled default with costs off; preserve this inactive default or retained value without claiming active cost rollup. Do not reject COST merely because costs=N when revenue=Y. Resolve to canonical code.

## Plan Class
CSV columns: PJO_PLAN_TYPE_PROJECT.csv.PlanClassCode

| Lookup Code | Meaning |
|---|---|
| BUDGET | Budget |
| FORECAST | Forecast |
| ORA_PROJ_PLAN | Financial Project Plan |

Authority: PJO_PLAN_CLASS, System configuration. The PROJECT_PLAN setup route hides this selector and initializes BUDGET. The task validation requires BUDGET for PROJECT_PLAN; reject other class intent as incompatible. Resolve to canonical code.

## Planning Amounts
CSV columns: PJO_PLAN_TYPE_PROJECT.csv.PlanOptionCode

| Lookup Code | Meaning |
|---|---|
| COST_AND_REV_SEP | Cost and revenue in separate plan versions |
| COST_AND_REV_TOGETHER | Cost and revenue in the same plan version |
| COST_ONLY | Cost only |
| REVENUE_ONLY | Revenue only |

Authority: PJO_PLAN_OPTION_CODE, System configuration. COST_ONLY is the established creation default. Other canonical members are not automatically authorized for a new PROJECT_PLAN: require branch/package evidence. Preserve evidenced existing combined/separate structure; do not infer parent code from the enable-revenue checkbox. Resolve to canonical code.

## Planning Amounts Row Scope
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlannedForCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode

| Lookup Code | Meaning |
|---|---|
| COST | Cost |
| COST_AND_REV_TOGETHER | Cost and revenue |
| REVENUE | Revenue |

Authority: PJO_PLANNED_FOR_CODE, System configuration. This child domain differs from parent PlanOptionCode. COST_ONLY parent has representative COST row; REVENUE_ONLY has REVENUE; separate has representative COST; combined retains COST_AND_REV_TOGETHER. Additional separate-revenue row cardinality needs current package evidence. Currency parent reference must equal its planning-options parent key. Resolve to canonical code.

## Additional Static Reference Scope

The following domains were corroborated against SB4 on 2026-09-17, including System customization level and complete code/meaning pairs. They need no runtime REST, database or FSM export. A finite domain proves membership only: it does not make a hidden control applicable or supply a missing CSV mapping. Financial-only tables are contextual reference material; they do not introduce active PROJECT_PLAN checks. Unknown supported eligibility remains unresolved/nonblocking. Preserve hidden, unrequested values.

## Yes or No
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanInMultiCurrFlag; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AllowFcstAmtCarryFlag; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenInclOpencommFlag; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AllowNegEtcFlag; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenRetManLineFlag; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ManualSpreadFlag; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.MapActSummaryFlag

| Lookup Code | Meaning |
|---|---|
| N | No |
| Y | Yes |

Authority: PJO_YES_NO, System configuration; complete lookup domain. Shared Boolean choices for Multiple Transaction Currencies, Carry Forward Unused Amounts, Open Commitments, Allow Negative ETC, Retain Manually Added Lines, Maintain Manual Spread, and Associate Actual Amounts to Summary Tasks. Apply only when the scoped field is applicable; preserve existing visibility, feature and disabled-field rules. Write Y or N. The two unmapped actual-update options do not acquire a CSV mapping from this table.

## Budgetary Control Resource Level
CSV columns: None; UI-only reference

| Lookup Code | Meaning |
|---|---|
| B | Both |
| L | Lowest resource |
| T | Top resource |

Authority: ORA_PJO_XCC_UI_RES_CTRL, System configuration; complete lookup domain. Top resource, Lowest resource and Both are finite membership choices. Both additionally requires the resource-budget opt-in. Preserve budgetary-control, planning-level and row applicability. There is no verified CSV destination; block the affected requested change as unsupported and not applied; continue only independent supported work without claiming the whole request complete.

## Budgetary Control Task Level
CSV columns: None; UI-only reference

| Lookup Code | Meaning |
|---|---|
| B | Both |
| L | Lowest task |
| T | Top task |

Authority: ORA_PJO_XCC_UI_TASK_CTRL, System configuration; complete lookup domain. Preserve task-budget opt-in, indexed-row, planning-level and budgetary-control predicates. There is no verified CSV destination; block the affected requested change as unsupported and not applied; continue only independent supported work without claiming the whole request complete.

## Budgetary Control Funding Source Level
CSV columns: None; UI-only reference

| Lookup Code | Meaning |
|---|---|
| P | Project |
| PRP | Project and resources at project |
| PRPRT | Project and resources at project and task |
| PTRPRT | Project and task and resources at project and task |
| RP | Resources at project |
| RPRT | Resources at project and task |
| RT | Resources at task |
| TRPRT | Task and resources at project and task |
| TRT | Task and resources at task |

Authority: ORA_PJO_XCC_UI_FS_CTRL, System configuration; complete lookup domain. Applicable shared controls require award calendar, budget class and enabled budgetary controls; feature, resource and task settings further constrain choices. Membership is static, but there is no verified CSV destination. Block the affected requested change as unsupported and not applied; continue only independent supported work without claiming the whole request complete.

## Budgetary Control Control Level
CSV columns: None; UI-only reference

| Lookup Code | Meaning |
|---|---|
| ABSOLUTE | Absolute |
| ADVISORY | Advisory |
| NO_CB | Do Not Create Control Budget |
| TRACK | Track |

Authority: PJO_CB_CONTR_LVL, System configuration; complete lookup domain. Resource rows apply their row-specific exclusions to this complete domain. Project rows allow ABSOLUTE, ADVISORY and TRACK only; exclude NO_CB. There is no verified CSV destination; block the affected requested change as unsupported and not applied; continue only independent supported work without claiming the whole request complete.

## Actual Amounts Through Period
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenActAmtsThruCode

| Lookup Code | Meaning |
|---|---|
| CURRENT_PERIOD | Current period |
| LAST_PERIOD | Last closed period |
| PRIOR_PERIOD | Prior period |

Authority: PJO_ACT_AMT_THRU, System configuration; complete lookup domain. Shared financial forecast generation reference only; excluded from ordinary PROJECT_PLAN setup. Serialize a code only after independent task applicability is established.

## Amount Scale
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.FactorByCode

| Lookup Code | Meaning |
|---|---|
| 1 | 1 |
| 10 | 10 |
| 100 | 100 |
| 1000 | 1,000 |
| 10000 | 10,000 |
| 100000 | 100,000 |
| 1000000 | 1,000,000 |

Authority: PJF_DISPLAY_FACTOR, System configuration; complete lookup domain. The Amount Scale control's visibility in shared financial reporting UI does not determine serialized requiredness. FactorByCode is mandatory in the PROJECT_PLAN planning-options import, including BUDGET class. The evidenced scoped create value is 1; preserve another supported explicit value. Output the code, not the comma-formatted meaning. See the defaulting matrix for create/update treatment.

## Budget Creation Method
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.BudgetCreationMethod

| Lookup Code | Meaning |
|---|---|
| DEFINE_SOURCE | Define source at creation |
| GENERATE | Generate from another source |
| MANUAL | Manually create budget lines |

Authority: ORA_PJO_BUDGET_CREATION_SETUP, System configuration; complete lookup domain. Shared FINANCIAL_PLAN/BUDGET generation reference only; excluded from ordinary PROJECT_PLAN setup. Enhanced creation settings and layout constrain applicability; this complete lookup domain does not assert exact control eligibility.

## Forecast Creation Method
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.BudgetCreationMethod

| Lookup Code | Meaning |
|---|---|
| COPY | Copy from another source |
| GENERATE | Generate from another source |
| MANUAL | Manually create forecast lines |

Authority: PJO_FORECAST_CREATION_METHOD, System configuration; complete lookup domain. Shared FINANCIAL_PLAN/FORECAST generation reference only; excluded from ordinary PROJECT_PLAN setup. Requires enhanced forecast and creation settings. The displayed forecast method writes the same stored creation-method field; never combine budget and forecast sets without resolving context. Exact control eligibility remains separate from static membership.

## Generation Source
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenSrcCode

| Lookup Code | Meaning |
|---|---|
| FINANCIAL_PLAN | Financial plan type |
| ORA_PROJECT_RES | Project Resources |
| PROJECT_PLAN | Project plan type |

Authority: PJO_PLAN_TYPE_CODE, System configuration; complete lookup domain. Shared financial generation reference only; excluded from ordinary PROJECT_PLAN setup. Award calendar A excludes ORA_PROJECT_RES. These codes choose the source category; they are not the dynamic financial-plan names supplied in Name4.

## Forecast Estimate-to-Complete Method
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodCode

| Lookup Code | Meaning |
|---|---|
| COST_PERF_INDEX_BASED | Cost performance index based |
| MANUAL_ENTRY | Manual entry |
| PLAN_TO_COMPLETE | Plan to complete |
| REMAINING_PLAN | Remaining plan |

Authority: PJO_PLAN_OVER_ETC_METHOD, System configuration; complete lookup domain. Shared FINANCIAL_PLAN/FORECAST generation reference only; excluded from ordinary PROJECT_PLAN setup. Generation-source/target flag Y excludes COST_PERF_INDEX_BASED. Never combine this domain with the project-plan Progress Estimate-to-Complete Method table.

## Source Plan Version — Financial Source
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenSrcPlanVerCode

| Lookup Code | Meaning |
|---|---|
| CURRENT_APPROVED | Current approved |
| CURRENT_BASELINED | Current baseline |
| CURRENT_WORKING | Current working |
| ORIGINAL_APPROVED | Original approved |
| ORIGINAL_BASELINED | Original baseline |

Authority: PJO_PLAN_VERSION_CODE, System configuration; complete lookup domain. Shared financial generation reference at PLAN_TYPE with FINANCIAL_PLAN source only; excluded from ordinary PROJECT_PLAN setup. Resolve the source branch first; output a code, not an actual version ID.

## Source Plan Version — Project Source
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenSrcPlanVerCode

| Lookup Code | Meaning |
|---|---|
| B | Baseline |
| W | Working |

Authority: PJO_PLAN_STATUS, System configuration; complete permitted subset. Shared financial generation reference at PLAN_TYPE with PROJECT_PLAN source only; excluded from ordinary PROJECT_PLAN setup. The permitted code subset is W and B. Any derived project-specific version identity remains dynamic and cannot be inferred from this local table.

## Report Cost
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.MarginDerivedFromCode

| Lookup Code | Meaning |
|---|---|
| B | Burdened cost |
| R | Raw cost |

Authority: PJO_MARGIN_DERIVED_FROM_CODE, System configuration; complete lookup domain. Shared financial reporting reference only; excluded from ordinary PROJECT_PLAN/BUDGET setup. Output B or R when independent applicability is established.

## Reporting Currency Type
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CurrencyType

| Lookup Code | Meaning |
|---|---|
| PC | Project currency |
| PFC | Project ledger currency |

Authority: PJO_REP_CURRENCY_TYPE, System configuration; complete lookup domain. Shared financial reporting reference only; excluded from ordinary PROJECT_PLAN/BUDGET setup. These currency-role codes are distinct from transaction currency codes.

## Forecast Rate Derivation Date Type
CSV columns: PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType

| Lookup Code | Meaning |
|---|---|
| EFFECTIVE_RATE_DATE | Effective resource rate dates |
| END_DATE_FORECAST | To date of forecast line |
| FIXED_DATE | Fixed date |
| START_DATE_FORECAST | From date of forecast line |
| SYSTEM_DATE | System date |

Authority: PJO_FCST_RATE_DRV_DATE_TYPE, System configuration; complete lookup domain. Shared FINANCIAL_PLAN/FORECAST reference only; excluded from ordinary PROJECT_PLAN setup. Never union these choices into the active project-plan or revenue budget date sets. Preserve the fixed-date companion requirement where this branch is applicable.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PJO.PPT.RESOLVE_LOVS | decision | 25 | evaluate_result | locally-resolved->PJO.PPT.DESIGN_GATE;live-required->PJO.PPT.LIVE_LOVS;unresolved-nonblocking->PJO.PPT.DESIGN_GATE;invalid->PJO.PPT.ROUTE_ISSUES | PJO.PPT.READINESS | stop | Evaluate supported local checks and record unsupported-reference warnings; select live-required whenever any supported live check remains, even when other checks are unresolved; otherwise continue to design |
| PJO.PPT.LIVE_LOVS | step | 26 | reference_lookup | resolved->PJO.PPT.DESIGN_GATE;unresolved-nonblocking->PJO.PPT.DESIGN_GATE;invalid->PJO.PPT.ROUTE_ISSUES | PJO.PPT.RESOLVE_LOVS | stop | Execute applicable Live Lookups through their declared read-only adapters, then evaluate dependent resolvers for supported references; no static field runs externally |
