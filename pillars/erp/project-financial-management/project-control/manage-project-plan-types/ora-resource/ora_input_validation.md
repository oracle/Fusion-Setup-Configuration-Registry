# Input Validation

The internal preparation request may include `copyConversionAttributes: true`
for an explicit shared-conversion action. This is not a CSV field or stored
checkbox. Resolve source rate/date values first; use the PLAN_TYPE mapping in
Design Enforcement. Independent conversion choices use normal row attributes
without this action. Preserve and preview all resulting `derivedChanges`.
The optional internal `sourceInput` retains the source-form business object.
Its `Curr_Set_Use_Conversion` control is translated by preparation and reconciled
against the ZIP using `finalData.sourceInput` at the preview gate; it is never
serialized as a CSV flag. Canonical-only callers without source-form input
continue to use the existing explicit action contract.

Preparation also supports explicit `insertRows` on an existing parent,
language-scoped `rename`, and `duplicateFrom` with optional `copyChildren` on a
create. These are internal action inputs, not new CSV headers. Use the contracts
in Design Enforcement and scripts/README.md; consultants supply business intent.

Accept codes, meanings, names, descriptions, translations and ordinary natural-language phrasing in any language when the evidence and context identify one valid member. Resolve intent to one CSV column first, then resolve its value. Do not require English, exact labels or prior knowledge of a code. Reject zero or multiple plausible matches from a supported authority; missing REST validation is unresolved/nonblocking under ora_reference_lookups.md, not evidence of an invalid value.

## Legacy Forecast Input Normalization

| Source input | Resolution | User guidance |
|---|---|---|
| Prog_Sett_Automatically_generate_fo omitted, empty or Remaining plan on ordinary create | No explicit forecast checkbox selection. Omit ProgAutoGenFcstVer from canonical requested choices so preparation materializes N from the scoped create default. Remaining plan belongs to EtcMethodCode; preserve the independently supplied ETC method. Retain original sourceInput and disclose the misplaced legacy value in the preview | Do not ask whether to enable automatic forecast generation or request a forecast financial plan type for this default |
| Explicit supported forecast checkbox choice | Resolve the explicit choice to canonical Y/N; preserve it over the create default. Y requires the selected forecast type in Name3 | Ask for the forecast type only when generation is explicitly enabled and its type is missing |
| No explicit forecast change on update or Duplicate, including misplaced Remaining plan | Preserve the existing or copied forecast setting; never apply the ordinary-create N default over it | A retained Y still requires its retained applicable Name3; resolve missing retained evidence through the selected workflow |
| Any other non-Boolean forecast value or conflicting explicit choices | Not covered by the legacy Remaining plan normalization; resolve the specific conflicting or invalid intent before preview | Do not silently replace an explicit unsupported choice with N |

## CSV Column Intent Resolution

Every exported column has one row below. Resolve business intent to the scoped column before validating its value. Flexfield segment labels require the configured context; raw segment numbers are not business aliases. Shared-page labels do not override task applicability.

| CSV Column | User Intent |
|---|---|
| PJO_PLAN_TYPE_PROJECT.csv.Name | Name |
| PJO_PLAN_TYPE_PROJECT.csv.ApprovedCostPlanTypeFlag | Designate as approved cost budget |
| PJO_PLAN_TYPE_PROJECT.csv.ApprovedRevPlanTypeFlag | Designate as approved revenue budget |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute1 | Descriptive flexfield segment 1 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute10 | Descriptive flexfield segment 10 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute11 | Descriptive flexfield segment 11 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute12 | Descriptive flexfield segment 12 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute13 | Descriptive flexfield segment 13 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute14 | Descriptive flexfield segment 14 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute15 | Descriptive flexfield segment 15 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute16 | Descriptive flexfield segment 16 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute17 | Descriptive flexfield segment 17 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute18 | Descriptive flexfield segment 18 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute19 | Descriptive flexfield segment 19 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute2 | Descriptive flexfield segment 2 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute20 | Descriptive flexfield segment 20 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute21 | Descriptive flexfield segment 21 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute22 | Descriptive flexfield segment 22 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute23 | Descriptive flexfield segment 23 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute24 | Descriptive flexfield segment 24 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute25 | Descriptive flexfield segment 25 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute26 | Descriptive flexfield segment 26 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute27 | Descriptive flexfield segment 27 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute28 | Descriptive flexfield segment 28 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute29 | Descriptive flexfield segment 29 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute3 | Descriptive flexfield segment 3 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute30 | Descriptive flexfield segment 30 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute4 | Descriptive flexfield segment 4 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute5 | Descriptive flexfield segment 5 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute6 | Descriptive flexfield segment 6 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute7 | Descriptive flexfield segment 7 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute8 | Descriptive flexfield segment 8 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.Attribute9 | Descriptive flexfield segment 9 (configured business label unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.AttributeCategory | Descriptive flexfield context |
| PJO_PLAN_TYPE_PROJECT.csv.AutoApproveFlag | Automatically approve forecasts |
| PJO_PLAN_TYPE_PROJECT.csv.AutoSubmitForAppr | Automatically submit forecasts for approval |
| PJO_PLAN_TYPE_PROJECT.csv.DefaultFinPlanTypeFlag | Set as default financial plan type |
| PJO_PLAN_TYPE_PROJECT.csv.Description | Description |
| PJO_PLAN_TYPE_PROJECT.csv.EnableWfFlag | Use workflow for status changes |
| PJO_PLAN_TYPE_PROJECT.csv.EndDate | To Date / End Date |
| PJO_PLAN_TYPE_PROJECT.csv.PlanClassCode | Plan Class |
| PJO_PLAN_TYPE_PROJECT.csv.PlanInMultiCurrFlag | Enable planning in multiple transaction currencies |
| PJO_PLAN_TYPE_PROJECT.csv.PlanOptionCode | Planning Amounts |
| PJO_PLAN_TYPE_PROJECT.csv.PlanTypeCode | Project Plan task branch |
| PJO_PLAN_TYPE_PROJECT.csv.PrimaryCostForecastFlag | Designate as primary cost forecast |
| PJO_PLAN_TYPE_PROJECT.csv.PrimaryRevForecastFlag | Designate as primary revenue forecast |
| PJO_PLAN_TYPE_PROJECT.csv.ReportQuantityFromCode | Report Quantity From Code (task UI intent unresolved) |
| PJO_PLAN_TYPE_PROJECT.csv.StartDate | From Date / Start Date |
| PJO_PLAN_TYPE_PROJECT.csv.DefaultAwdFinPlanTypeFlag | Set as default award financial plan type |
| PJO_PLAN_TYPE_PROJECT.csv.BudgetaryControlsFlag | Enable budgetary controls |
| ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv.PJO_PLAN_TYPE_PROJECT.Name | Parent project plan type name |
| ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv.SetCode | Set Assignments: Code / reference data set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PJO_PLAN_TYPE_PROJECT.Name | Parent project plan type name |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlannedForCode | Planning Amounts scope of this options row |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AllowFcstAmtCarryFlag | Carry forward unused amounts from past periods / Carry Forward Unused Amounts from Past Periods |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AllowNegEtcFlag | Allow negative ETC calculation |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ApprovedCostPlanTypeFlag | Approved Cost Plan Type Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ApprovedRevPlanTypeFlag | Approved Rev Plan Type Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute1 | Descriptive flexfield segment 1 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute10 | Descriptive flexfield segment 10 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute11 | Descriptive flexfield segment 11 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute12 | Descriptive flexfield segment 12 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute13 | Descriptive flexfield segment 13 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute14 | Descriptive flexfield segment 14 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute15 | Descriptive flexfield segment 15 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute16 | Descriptive flexfield segment 16 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute17 | Descriptive flexfield segment 17 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute18 | Descriptive flexfield segment 18 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute19 | Descriptive flexfield segment 19 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute2 | Descriptive flexfield segment 2 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute20 | Descriptive flexfield segment 20 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute21 | Descriptive flexfield segment 21 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute22 | Descriptive flexfield segment 22 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute23 | Descriptive flexfield segment 23 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute24 | Descriptive flexfield segment 24 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute25 | Descriptive flexfield segment 25 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute26 | Descriptive flexfield segment 26 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute27 | Descriptive flexfield segment 27 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute28 | Descriptive flexfield segment 28 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute29 | Descriptive flexfield segment 29 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute3 | Descriptive flexfield segment 3 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute30 | Descriptive flexfield segment 30 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute4 | Descriptive flexfield segment 4 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute5 | Descriptive flexfield segment 5 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute6 | Descriptive flexfield segment 6 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute7 | Descriptive flexfield segment 7 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute8 | Descriptive flexfield segment 8 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Attribute9 | Descriptive flexfield segment 9 (configured business label unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AttributeCategory | Descriptive flexfield context |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AutoApproveFlag | Auto Approve Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AutoBdgtBaseline | Automatically designate budget version as baseline |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AutoRollupTaskDate | Automatically Roll Up Task Planned Dates |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.BudgetCreationMethod | Forecast Creation Method |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CommitmentControlFlag | Commitment Control Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CumulativeBudgetOption | Cumulative Budget Option (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CurrencyType | Currency Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CurrentPlanningPeriod | Current Planning Period |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EnableCostsForProjPlan | Enable costs for project plan |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EnableRevForProjPlan | Enable revenue for project plan |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodCode | Estimate-to-Complete Method |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodFlag | Etc Method Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ExlDispBslnPlanValues | Exl Disp Bsln Plan Values (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ExlDispCommittments | Display commitments |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ExlDispCurConMultTra | Display currency conversion attributes and amounts in multiple transaction currencies |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ExlDispPlanVerCompVal | Exl Disp Plan Ver Comp Val (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ExlPeriodicLayout | Exl Periodic Layout (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.FactorByCode | Amount Scale |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ForecastPeriodName | Forecast Period Name (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenActAmtsThruCode | Actual Amounts Through Period |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenBdgtDuringBaseline | Generate budget version when setting baseline for project plan |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenInclBillEventFlag | Gen Incl Bill Event Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenInclOpencommFlag | Open commitments |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenOvrEtcMethodCode | Gen Ovr Etc Method Code (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenOvrEtcMthdFlag | Gen Ovr Etc Mthd Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenRetManLineFlag | Retain Manually Added Forecast Lines / Retain Manually Added Budget Lines |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenSrcCode | Generation Source / ETC Generation Source / Generation Source |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.GenSrcPlanVerCode | Source Plan Version |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.IntegrationType | Integration Type (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.MarginDerivedFromCode | Report Cost |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDate | Rate Derivation Date (fixed-date selection) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType | Rate Derivation Date Type (project-plan options) / Bill Rate Derivation Date Type (revenue row) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ObjectTypeCode | Planning object type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateDate | Cost, Project Currency: Fixed Date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateDateType | Cost, Project Currency: Date Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateType | Cost, Project Currency: Rate Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateDate | Revenue, Project Currency: Fixed Date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateDateType | Revenue, Project Currency: Date Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateType | Revenue, Project Currency: Rate Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompCalcMethod | Physical Percent Complete Calculation Method |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompRollupMethod | Primary Physical Percent Complete Basis |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateDate | Cost, Ledger Currency: Fixed Date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateDateType | Cost, Ledger Currency: Date Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateType | Cost, Ledger Currency: Rate Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateDate | Revenue, Ledger Currency: Fixed Date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateDateType | Revenue, Ledger Currency: Date Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateType | Revenue, Ledger Currency: Rate Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanInMultiCurrFlag | Multiple Transaction Currencies |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanLevelCode | Planning Level |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanOptionLevelCode | Planning options level |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanTypeCode | Project Plan task branch |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PrimaryCostForecastFlag | Primary Cost Forecast Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PrimaryRevForecastFlag | Primary Rev Forecast Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ProgAutoApprFcstVer | Automatically approve forecast |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ProgAutoGenFcstVer | Automatically generate forecast version |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ProgUpdPlanQtyWithEac | Update planned quantity with EAC quantity |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RaTaskDatesSame | Use task planned dates as task assignment dates |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RetOverRatesFrmSrcFlag | Ret Over Rates Frm Src Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevClassificationMethod | Revenue Calculation Method |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.SpecPcCostAtProjLevel | Spec Pc Cost At Proj Level (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.SpecPcRevAtProjLevel | Spec Pc Rev At Proj Level (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.SpecPfcCostAtProjLevel | Spec Pfc Cost At Proj Level (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.SpecPfcRevAtProjLevel | Spec Pfc Rev At Proj Level (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.SyncTaskTxnPlanDates | Synchronize Task Transaction Dates with Planned Dates |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.SyncTxnDateBuffer | Date Adjustment Buffer in Days |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode | Calendar Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.UsePlanningRatesFlag | Use Planning Rates |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.UseThirdPartySoftware | Use third-party software for scheduling / Microsoft Project scheduling |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name | Period Profile |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name1 | Planning Resource Breakdown Structure |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.VersionNumber | Planning Resource Breakdown Structure Version |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name2 | Financial Plan Type for Budget Generation |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name3 | Forecast Financial Plan Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name4 | Generation Source Financial Plan Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AllQtyFlag | All Qty Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AmountSetTypeCode | Amount-set planning scope; COST for the scoped COST child |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.BillRateFlag | Bill Rate Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.BrdndCostFlag | Allow burdened cost amounts in the amount set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.BrdndRateFlag | Brdnd Rate Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CostQtyFlag | Allow cost quantities in the amount set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.CostRateFlag | Cost Rate Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RawCostFlag | Allow raw cost amounts in the amount set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevenueFlag | Allow revenue amounts in the amount set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevenueQtyFlag | Allow revenue quantities in the amount set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RetainSourceSpreadFlag | Retain Source Spread Flag (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateDate | Cost, Planning Currency: Fixed Date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateDateType | Cost, Planning Currency: Date Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateType | Cost, Planning Currency: Rate Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateDate | Revenue, Planning Currency: Fixed Date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateDateType | Revenue, Planning Currency: Date Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateType | Revenue, Planning Currency: Rate Type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AutoPlanAsmtFlag | Set unplanned assignments as planned assignments |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AsgnResInSingleCurrFlag | Assign Resource in Single Currency for a Task |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.ManualSpreadFlag | Maintain manual spread on date changes |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.MapActSummaryFlag | Associate project costs or revenue to summary tasks / Associate project costs to summary tasks / Associate project revenue to summary tasks |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.PJO_PLAN_TYPE_PROJECT.Name | Parent project plan type name |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.ShortCode | Business Unit |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.UsePlanningRatesFlag | Use planning rates for this business-unit row; independent of the general planning-option field |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.IndSchName | Burden Schedule |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName | Resource Class Raw Cost Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName1 | Resource Class Bill Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName2 | Person Cost Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName3 | Job Cost Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName4 | Nonlabor Resource Cost Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName5 | Person Bill Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName6 | Job Bill Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName7 | Nonlabor Resource Bill Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.SysEffectiveDate | Sys Effective Date (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName8 | Project Role Cost Rate |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName9 | Project Role Bill Rate |
| PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv.PJO_PLAN_TYPE_PROJECT.Name | Parent project plan type name |
| PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv.Description | Translated description |
| PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv.Language | Translation language |
| PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv.Name | Translated project plan type name |
| PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv.SourceLang | Source language |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PJO_PLAN_TYPE_PROJECT.Name | Parent project plan type name |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode | Parent planning amounts scope |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TxnCurrencyCode | Transaction Currency Code |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PcCostExchangeRate | Pc Cost Exchange Rate (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PcRevExchangeRate | Pc Rev Exchange Rate (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PfcCostExchangeRate | Pfc Cost Exchange Rate (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PfcRevExchangeRate | Pfc Rev Exchange Rate (task UI intent unresolved) |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TransCurrencyName | Transaction Currency Name |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.Name | Name (task UI intent unresolved) |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Project plan type identity | Name and create/update intent | Block preview | Resolve one project-plan record; request only the missing identity | Create or update | resolve_existing_plan_type |
| Availability dates | StartDate; optional EndDate | Block if mandatory StartDate missing | Accept a clear user date and normalize to the exported date representation; EndDate must not precede StartDate | Create or explicit date change |  |
| Planning row context | PlanTypeCode, PlanOptionLevelCode, PlannedForCode and parent Name | Block ambiguous branch | Use task PROJECT_PLAN and PLAN_TYPE context plus the evidenced parent/child planning amounts relationship before contextual LOVs | Any planning-options row |  |
| Serialized import contract | Actual immutable ZIP bytes; explicit create or update operation | Block preview and approval on every missing or invalid mandatory value | Run scripts/validate_import.py in this task folder; aggregate all member, row and attribute findings before correction. A narrative passed result cannot satisfy this gate | Every prepared import |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Dynamic reference has no supported validation route | Warning, nonblocking | Follow Unresolved Validation Policy in ora_reference_lookups.md; preserve proven supplied representation and continue supported checks | |
| Period Profile supplied or changed | Resolve when evidenced; otherwise warning, nonblocking | Follow resolve_period_profile and its Period Profile Evidence Boundary; historical tables alone cannot establish a target mismatch | resolve_period_profile |
| Existing seed-data or attached record selected | Verify | Check protection per requested field; do not infer blanket editability from record existence | resolve_existing_plan_type |
| Output units calculation requested without feature readiness | Warning, nonblocking | Record unverified feature state and preserve ORA_OUTPUT_UNITS. Known disabled remains incompatible; never downgrade the request | resolve_percent_calc |
| Applicable input contract is satisfied | Ready | Continue to dependency and LOV resolution |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Name and description shape | Require Name; validate schema lengths from the target contract; Description optional. Check duplicate identity in current data, not a header-only template | Create or update | resolve_existing_plan_type |
| Shared yes/no domain | Resolve the applicable scoped Boolean field through the local Yes or No table; preserve omitted and disabled fields. Existing task applicability gates remain required | A supplied field belongs to the Yes or No table scope and its applicability is proven | resolve_yes_no |
| Boolean control input | Accept natural-language yes/no in any language when unambiguous and serialize canonical Y/N; preserve omitted optional values | A proven Boolean control is supplied |  |
| Final serialized values | Resolve business wording before packaging; the byte validator requires canonical codes in the final CSV. It validates and never supplies defaults or rewrites explicit choices | Every prepared import |  |
| Calendar and rate date | Resolve TimePhasedCode before NtpRateDateType. G/P permits start-of-line or effective resource rate dates only; N permits the wider row-specific domain. Do not apply this restriction to the separate currency conversion date controls | Rate derivation supplied or changed | resolve_rate_derivation |
| Generation target names | GenBdgtDuringBaseline=Y requires selected budget Name2 even if AutoBdgtBaseline=N. ProgAutoGenFcstVer=Y requires selected forecast Name3. Missing business choices block; unavailable dynamic membership lookup remains a disclosed warning | Budget or forecast generation enabled | |
| Per-business-unit rate mode | Use PJO_PPT_PLAN_OPTION_RATE_SCH.csv.UsePlanningRatesFlag for that row, not the similarly named general-options field. Resolve mode before requested schedules. Actual-rate fallback schedules remain supported; inactive retained schedules are preserved and disclosed rather than silently cleared | Rate row or schedules supplied | |
| Missing required default | Report UNRESOLVED_REQUIRED_INPUT with exact CSV member, row, attribute, branch and missing/blank state when no evidenced default or explicit value is available. This is missing payload input, not a nonblocking reference-membership warning | Required create or conditional value missing |  |
| Update preservation | Do not fill omitted update columns with create defaults. An omitted column and a present empty cell are different inputs; do not treat a blank required field as N or as preserve. Validate explicit values and require enough unchanged context to evaluate a changed conditional field | Update |  |
| Amount-set import tuple | Validate all ten imported amount-set elements, including six nonblank mandatory attributes. Apply the scoped create matrix only during package preparation; these defaults are not hard constraints on explicit choices. On update, materialize retained tuple values because importer reads are unconditional | Submitted planning-options row |  |
| Explicit amount-set type | COST is the evidenced scoped creation value. Equality with PlannedForCode is not a proven import invariant; preserve an explicit alternative and report deferred amount-set compatibility rather than silently replacing it | Explicit amount-set type differs from scoped initialization |  |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.AutoBdgtBaseline | Required even when the control is disabled. Y requires GenBdgtDuringBaseline=Y and selected budget plan type Name2; known budgetary control disablement is incompatible. Unknown target feature/editability evidence remains disclosed | Create or explicit value supplied |  |
| Column and branch identity | Resolve one scoped column before its value. Preserve parent keys and task/row scope; do not map similar NameN headers by numbering | Any field supplied |  |
| Separate planning code | Apply this check to normalized business intent before export or lookup, including prose and structured fields such as planning_code, separate_planning_code or business_planning_code. A supplied separate code fails with UNSUPPORTED_PLANNING_CODE. No standard task CSV or service mapping is established. PlanTypeCode is PROJECT_PLAN, not this code. Do not drop the requirement, append it to Name or Description, or invent a column. A configured DFF needs a separately verified context/segment contract and is not an automatic workaround. | A separate business planning code is requested, in any language |  |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.TimePhasedCode | Calendar Type: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_calendar |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType | Rate Derivation Date Type: use the dedicated resolver after resolving calendar; serialize canonical code. | Supplied or changed in the PROJECT_PLAN COST or COST_AND_REV_TOGETHER child context | resolve_rate_derivation |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.NtpRateDateType | Bill Rate Derivation Date Type: use the dedicated resolver; serialize canonical code. | Supplied or changed in the REVENUE child context, BUDGET class, non-time-phased branch | resolve_budget_rate_date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlanLevelCode | Planning Level: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_plan_level |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RevClassificationMethod | Revenue Calculation Method: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_rev_classification |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateDateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateDateType | Currency Conversion Date Type: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_conversion_date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompCalcMethod | Physical Percent Complete Calculation Method: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_percent_calc |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.EtcMethodCode | Estimate-to-Complete Method: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_progress_etc |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PercentCompRollupMethod | Primary Physical Percent Complete Basis: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_percent_rollup |
| PJO_PLAN_TYPE_PROJECT.csv.PlanClassCode | Plan Class: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_plan_class |
| PJO_PLAN_TYPE_PROJECT.csv.PlanOptionCode | Planning Amounts: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_plan_option |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PlannedForCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode | Planning Amounts Row Scope: use the dedicated resolver; serialize canonical code. | The scoped field is supplied or changed | resolve_planned_for |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TxnCurrencyCode; PJO_PPT_PLAN_OPTION_CUR_SETTING.csv.TransCurrencyName | Transaction Currency: use the dedicated resolver; serialize CURRENCY_CODE to TxnCurrencyCode; authoritative NAME to TransCurrencyName. | The scoped field is supplied or changed | resolve_currency |
| ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv.SetCode | Reference Data Set: use the dedicated resolver; serialize SetCode; never numeric SetId. | The scoped field is supplied or changed | resolve_set |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name | Period Profile: use resolve_period_profile and its evidence boundary; write a name, never an ID. Preserve an unambiguous supplied name when target identity or compatibility is unresolved. | The scoped field is supplied or changed | resolve_period_profile |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PcRevRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.PfcRevRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchCostRateType; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.RateSchRevRateType | Currency Conversion Rate Type: use the dedicated resolver; serialize ConversionTypeId canonical code. | The scoped field is supplied or changed | resolve_conversion_type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name3 | Forecast Financial Plan Type: use the dedicated resolver; preserve supplied display name with unresolved/nonblocking status when validation is unsupported; never infer ID. | The scoped field is supplied or changed | resolve_forecast_type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name2 | Target Financial Plan Type: use the dedicated resolver; preserve supplied display name with unresolved/nonblocking status when validation is unsupported; never infer ID. | The scoped field is supplied or changed | resolve_ra_plan_type |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.ShortCode | Business Unit: use the dedicated resolver and its verified canonical ShortCode mapping; never serialize the numeric BU ID. | The scoped field is supplied or changed | resolve_business_unit |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName1 | Resource Class Planning Rate Schedule: use the dedicated resolver; serialize exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally. | Scoped fallback or planning schedule supplied for this business-unit row; bill schedules require a revenue branch | resolve_resclass_schedule |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName2; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName5 | Employee Planning Rate Schedule: use the dedicated resolver; serialize exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally. | Planning rates are enabled and the scoped schedule is supplied; bill schedules additionally require a revenue branch | resolve_employee_schedule |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName3; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName6 | Job Planning Rate Schedule: use the dedicated resolver; serialize exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally. | Planning rates are enabled and the scoped schedule is supplied; bill schedules additionally require a revenue branch | resolve_job_schedule |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName4; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName7 | Non-Labor Planning Rate Schedule: use the dedicated resolver; serialize exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally. | Planning rates are enabled and the scoped schedule is supplied; bill schedules additionally require a revenue branch | resolve_nonlabor_schedule |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName8; PJO_PPT_PLAN_OPTION_RATE_SCH.csv.RateScheduleName9 | Project Role Planning Rate Schedule: use the dedicated resolver; serialize exact RATE_SCHEDULE_NAME for the scoped cost/bill column; retain ID internally. | Scoped schedule supplied for this business-unit row; actual-rate Project Role Cost Rate is target-observed; bill schedules require supported revenue context | resolve_role_schedule |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv.IndSchName | Burden Schedule: use the dedicated resolver; serialize canonical Name; never schedule ID. | Planning rates are enabled and Burden Schedule is supplied | resolve_burden_schedule |
| Task Settings date buffer | SyncTxnDateBuffer is optional business input. With SyncTaskTxnPlanDates=Y, preparation materializes 0 when the effective value is empty on create/update; explicit integers override retained values and omitted nonempty retained buffers are preserved. An active blank in final ZIP bytes returns UNMATERIALIZED_DEFAULT; it requires preparation, not more business input. Validate nonempty active values as integers. With N, preserve the inactive buffer. No unsupported minimum/maximum is imposed | Submitted Task Settings row | |
| FIXED_DATE companions | For each scoped conversion RateDateType, pair its same-prefix RateDate column; validate a supplied date. Conversion-date requiredness follows the corresponding enabled context, including project-level override flags. NtpRateDate is required when NtpRateDateType=FIXED_DATE; block that incomplete request instead of inventing a date. | A fixed-date member resolves |  |
| DFF and translations | Resolve configured DFF context/segment labels and translation representation before changes; preserve omitted fields. Missing dynamic membership authority follows the nonblocking unresolved policy; the template does not define their value sets. | DFF or translation values supplied |  |
| Unmapped or hidden field | Block a requested change when intent, domain or PROJECT_PLAN applicability remains unproven; preserve existing values for unrequested fields. No UI LOV is not permission to skip validation. | No verified mapping or applicability in this task |  |

## CSV and UI Mismatch Gates

| CSV Scope or UI Field | Required Resolution |
|---|---|
| Separate business planning code | Unsupported by the verified standard package contract. Resolve the business-design requirement before acquisition or preview; a routine waiver cannot make an unmapped field supported. |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name1; PJO_PPT_PLAN_OPTION_GEN_OPT.csv.VersionNumber | Dynamic RBS name/version; the visible selector is PLAN_VERSION-only, so it is not required for ordinary setup. Missing REST membership/pairing validation is unresolved/nonblocking; preserve the provided name/version where import applicability is proven. Unknown import applicability is a separate mapping issue. |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv.Name4 | Dynamic generation-source financial plan type; visible selectors are FINANCIAL_PLAN-only, but the PROJECT_PLAN importer explicitly resolves this name to the generation-source ID. Import representation is supported; current eligible type authority and an equivalent setup lookup remain unresolved/nonblocking. Preserve the supplied Name4 and disclose skipped membership validation. |
| Budgetary-control resource/task/funding-source levels, default rate type, and ControlLevelCode selectors | Local static tables resolve the resource, task, funding-source and control-level domains; default rate type remains dynamic. No corresponding child CSV exists. A missing mapping blocks that requested change; label it unsupported and not applied, and continue independent supported work without claiming the whole request complete. Do not serialize them into BudgetaryControlsFlag or any invented column. |
| Shared-page financial-plan-only controls | The broader UI inventory is not PROJECT_PLAN authorization. Preserve hidden/unrequested fields; resolve requested exceptions from task-specific evidence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PJO.PPT.VALIDATE_INPUT | step | 10 | validate_input | valid->PJO.PPT.READINESS;invalid->PJO.PPT.INPUT_ISSUES | PJO.PPT.DEFAULTS | stop | Any assisted request for Manage Project Plan Types |
