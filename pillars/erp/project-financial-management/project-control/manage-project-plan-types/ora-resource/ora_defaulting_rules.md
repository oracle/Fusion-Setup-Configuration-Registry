# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Plan class | BUDGET | New PROJECT_PLAN with omitted class; supported setup initialization | No | resolve_plan_class |
| Exact parent and child attributes in the matrix below | Only the evidenced per-field value | New row in the stated branch and no explicit choice | No | |
| Start date | Customer-supplied effective date; otherwise current target business date after confirmation | New plan type | No | |
| Project plan type option | COST_ONLY | New PROJECT_PLAN with omitted planning amounts; supported setup initialization | No | resolve_plan_option |
| Date Adjustment Buffer in Days | 0 | Submitted planning-options row on create or update, SyncTaskTxnPlanDates=Y and the effective SyncTxnDateBuffer is empty after merging explicit and retained values | No; explicit integers and retained nonempty buffers take precedence | |

Preserve user-supplied values and validate their applicability. The class and planning-amount defaults are proven setup initialization; they are not a claim that an import silently supplies omitted columns. Materialize required values through the validated package contract. Do not infer additional child rows, conditional option defaults, reference identities, DFF values or translations.

## Serialized Field Default Matrix

Scope: new PROJECT_PLAN / BUDGET / COST_ONLY parent with a COST planning-options
child. Required means non-null entity metadata intersected with the exported
CSV contract, not merely a visible UI asterisk. Materialize these fields before
byte validation; the validator never fills them. Explicit valid choices win over
every default below. Do not apply these create defaults to updates.

Evidence keys: E1 = parent entity required/default metadata; E2 = child planning
entity required/default metadata; E3 = amount-set entity required/default
metadata; D1 = scoped create initialization; I1 = import service skips UI
initialization; I2 = importer consumes all ten amount-set elements. The source
scope is FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64, snapshot 260917.0749.S,
intersected with the six-member, 213-column FSM template at release
11.13.27.01.0. This is authoring provenance, not proof of deployed-target parity.
Current target exports still establish the member/header contract. Observed
target rows never establish defaults, requiredness or universal membership.

| Evidence key | Source within financialPlanOptions | Supported fact and limit |
|---|---|---|
| E1 | protectedModel/entity/PlanTypeEO.xml, attribute definitions at lines 111–269 and 681 | Parent required/default metadata; exclude internal IDs and audit attributes from CSV requirements |
| E2 | protectedModel/entity/PlanningOptionEO.xml, attribute definitions at lines 528–1746 | Child required/default metadata; joined read-only NameN attributes do not establish unconditional CSV requiredness |
| E3 | protectedModel/entity/AmountSetEO.xml, attribute definitions at lines 126–234 | Six nonblank amount-set attributes; nullable attributes remain subject to the importer element contract |
| D1 | protectedModel/entity/PlanningOptionEOImpl.java, defaultCrPlTypePlOptions at lines 6610–6738 and amount-set construction at 9006–9020 | Scoped creation defaults; preserve explicit supported alternatives instead of enforcing defaults as invariants |
| I1 | protectedModel/entity/PlanTypeEOImpl.java, lines 408–412 and 642–643 | ProjectPlanTypeServiceAM skips UI child creation/defaulting; UI initialization does not supply omitted import values |
| I2 | PlanTypeService/applicationModule/PlanTypeBusinessObjectAMImpl.java, lines 300–342 | Importer reads all ten amount-set XML elements; CSV omission-to-XML behavior remains unverified |

The source base is
fusionapps/prj/components/projectsFinancials/control/financialPlanOptions/.
Source paths are citations, never runtime prerequisites. Server acceptance and
generic sparse-update semantics must not be inferred from these citations.

| CSV Member | Attribute | Requirement | Context | Create default | Evidence / explicit input |
|---|---|---|---|---|---|
| PJO_PLAN_TYPE_PROJECT.csv | Name | Create-required | Parent identity | None | E1; explicit business name |
| PJO_PLAN_TYPE_PROJECT.csv | StartDate | Create-required | Parent availability | None in importer | E1/I1; business date or explicitly selected target business date |
| PJO_PLAN_TYPE_PROJECT.csv | PlanTypeCode | Create-required | Parent task branch | PROJECT_PLAN | Task identity; never a business planning code |
| PJO_PLAN_TYPE_PROJECT.csv | PlanClassCode | Create-required | Parent class | BUDGET | E1/D1; another branch needs independent applicability evidence |
| PJO_PLAN_TYPE_PROJECT.csv | PlanOptionCode | Create-required | Parent planning amounts | COST_ONLY | D1; preserve an explicitly selected supported branch |
| PJO_PLAN_TYPE_PROJECT.csv | PlanInMultiCurrFlag | Create-required | Parent currency context | N | E1; explicit Y requires compatible child context |
| PJO_PLAN_TYPE_PROJECT.csv | EnableWfFlag | Create-required | Parent workflow | N | E1; preserve explicit supported choice |
| PJO_PLAN_TYPE_PROJECT.csv | DefaultFinPlanTypeFlag | Create-required | Parent default designation | N | E1; do not copy another plan type's designation |
| PJO_PLAN_TYPE_PROJECT.csv | AutoApproveFlag | Create-required | Parent approval | N | E1; preserve explicit supported choice |
| PJO_PLAN_TYPE_PROJECT.csv | DefaultAwdFinPlanTypeFlag | Create-required | Parent award designation | N | E1; not inferred from ordinary project default designation |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PJO_PLAN_TYPE_PROJECT.Name | Required identity | Child-to-parent link | Selected parent Name | Exported key; never copy another parent's name |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PlanOptionLevelCode | Create-required | Child setup level | PLAN_TYPE | E2/D1; not PLAN_VERSION |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | ObjectTypeCode | Create-required | Child object context | PROJECT | E2/D1 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PlanTypeCode | Create-required | Child task branch | PROJECT_PLAN | E2/D1; generic entity default FINANCIAL_PLAN is wrong for this task |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PlannedForCode | Create-required | COST_ONLY parent child | COST | E2/D1; derive from this branch, not a universal child default |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PlanInMultiCurrFlag | Create-required | PROJECT_PLAN child | N | E2/D1; preserve consistent explicit parent/child choice |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AllowFcstAmtCarryFlag | Create-required | Child carry-forward option | N | E2/D1 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | FactorByCode | Create-required | Child amount scale, including hidden UI | 1 | E2/D1; preserve another supported explicit scale |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SpecPcRevAtProjLevel | Create-required | Child project-currency revenue override | N | E2; independent field, not inherited from parent |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SpecPfcRevAtProjLevel | Create-required | Child ledger-currency revenue override | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SpecPcCostAtProjLevel | Create-required | Child project-currency cost override | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SpecPfcCostAtProjLevel | Create-required | Child ledger-currency cost override | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SyncTaskTxnPlanDates | Create-required | Child task-date synchronization | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | GenBdgtDuringBaseline | Create-required | Child budget generation | N | E2/D1 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AutoBdgtBaseline | Create-required | Child generated-budget baseline designation | N | E2/D1; Y requires generation and an applicable selected budget plan type |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | UseThirdPartySoftware | Create-required | Child integration option | N | E2; explicit enablement affects editability |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AutoRollupTaskDate | Create-required | Child task-date rollup | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | RaTaskDatesSame | Create-required | Child task/assignment dates | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | UsePlanningRatesFlag | Create-required | Child planning rates | N | E2; preserve explicit supported choice |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | EnableCostsForProjPlan | Create-required | Child cost planning | N | E2; COST amount-set capabilities do not force this flag to Y |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AllowNegEtcFlag | Create-required | Child negative ETC | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | ProgAutoApprFcstVer | Create-required | Child progress forecast approval | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | ProgAutoGenFcstVer | Create-required | Child progress forecast generation | N | E2; ordinary create defaults to disabled without asking. The legacy source value Remaining plan is ETC intent, not forecast enablement; follow Legacy Forecast Input Normalization in Input Validation. Explicit Y/N overrides; updates and duplicates retain their current/source setting |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | ProgUpdPlanQtyWithEac | Create-required | Child EAC quantity update | N | E2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AmountSetTypeCode | Create-required | COST child's amount-set key | COST | E3/D1/I2; derived from PlannedForCode in scoped initialization |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | RawCostFlag | Create-required | COST amount-set raw cost entry | Y | E3 default N is overridden by scoped D1; not a universal Boolean default |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | CostQtyFlag | Create-required | COST amount-set cost quantity entry | Y | E3 default N is overridden by scoped D1 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | BrdndCostFlag | Create-required | COST amount-set burdened cost entry | Y | E3 default N is overridden by scoped D1 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | RevenueFlag | Create-required | COST amount-set revenue amount entry | N | E3/D1; preserve explicit supported choices rather than forcing defaults |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | RevenueQtyFlag | Create-required | COST amount-set revenue quantity entry | N | E3/D1 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AllQtyFlag | Import element required; entity nullable | Submitted amount-set tuple | N | D1/I2; do not omit element solely because entity is nullable |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | BillRateFlag | Import element required; entity nullable | Submitted amount-set tuple | N | D1/I2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | CostRateFlag | Import element required; entity nullable | Submitted amount-set tuple | Y | D1/I2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | BrdndRateFlag | Import element required; entity nullable | Submitted amount-set tuple | Y | D1/I2 |

The ten amount-set attributes are a composite imported configuration. The
scoped create defaults above explain the observed COST/Y/Y/Y/N/N tuple without
turning it into an invariant: requiredness and canonical Y/N membership do not
authorize overwriting explicit choices. The four entity-nullable attributes
still have unguarded importer reads. Materialize them from scoped create input
or retained update evidence; do not invent CSV-to-XML omission semantics.

## Conditional and Optional Inputs

| CSV Member | Attribute | Requirement | Context | Default / explicit input |
|---|---|---|---|---|
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | Name2 | Conditional | GenBdgtDuringBaseline=Y, including when AutoBdgtBaseline=N | No default; selected applicable budget financial plan type; automatic baseline additionally requires generation enabled |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | Name3 | Conditional | ProgAutoGenFcstVer=Y | No default; selected applicable forecast financial plan type, independently of the budget Name2 |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | NtpRateDate | Conditional | NtpRateDateType=FIXED_DATE | Explicit date; no invented current date |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SyncTxnDateBuffer | Optional business input; materialize save default | SyncTaskTxnPlanDates=Y | Effective empty value becomes 0 on create/update; explicit integers override and retained nonempty values are preserved. With N, leave the inactive buffer unchanged |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PcCostRateDate; PcRevRateDate; PfcCostRateDate; PfcRevRateDate; RateSchCostRateDate; RateSchRevRateDate | Conditional | Corresponding active currency context and same-prefix RateDateType=FIXED_DATE | Explicit date; PLAN_VERSION-only requiredness must not be imposed on PLAN_TYPE |
| ORA_PJO_PROJ_PLAN_TYPE_SET_ASMT.csv | PJO_PLAN_TYPE_PROJECT.Name; SetCode | Required identity when row supplied | Set assignment | No default or inferred target identity |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv | PJO_PLAN_TYPE_PROJECT.Name; ShortCode | Required identity when row supplied | Business-unit rate settings | No default; other schedule columns are optional unless the selected rate configuration requires them |
| PJO_PLAN_TYPE_PROJECT_TRANSLATION.csv | PJO_PLAN_TYPE_PROJECT.Name; Language | Required identity when row supplied | Requested translation | No default; never clone unrelated translations |
| PJO_PPT_PLAN_OPTION_CUR_SETTING.csv | PJO_PLAN_TYPE_PROJECT.Name; PJO_PPT_PLAN_OPTION_GEN_OPT.PlannedForCode; TxnCurrencyCode | Required identity when row supplied | Requested child currency | No default; exact parent and child keys |
| PJO_PLAN_TYPE_PROJECT.csv | ApprovedCostPlanTypeFlag; ApprovedRevPlanTypeFlag; AutoSubmitForAppr; PrimaryCostForecastFlag; PrimaryRevForecastFlag; BudgetaryControlsFlag | Not unconditionally create-required in inspected entity | Optional/branch-dependent parent settings | No blanket N default; preserve or obtain applicable business choice |
| PJO_PLAN_TYPE_PROJECT.csv | Description; EndDate; ReportQuantityFromCode; AttributeCategory; Attribute1 through Attribute30 | Optional unless separately configured | Parent descriptive/extension data | No default; date ordering and configured DFF requirements remain applicable |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | Remaining columns listed in CSV Column Intent Resolution | No unconditional requirement established here | Optional or conditional on separately evidenced requested feature | Use the observed UI defaults below only in their stated create context; otherwise no inferred default. Preserve unrequested values and disclose unsupported checks |

## Blank, Omitted and Update Preservation

| Input state | Create | Update |
|---|---|---|
| Explicit N | A real canonical negative choice; never missing | Preserve and validate applicability; do not replace with a create default |
| Explicit Y or another valid canonical choice | Preserve; defaults are not constraints | Preserve subject to supported relationship and editability checks |
| Present empty cell | Not N; fails a mandatory value check even when entity metadata declares a default | Do not interpret as preservation; required blank values fail. Optional clearing needs verified importer semantics |
| Omitted column | Materialize required values before preview; unknown default becomes UNRESOLVED_REQUIRED_INPUT | Do not add create defaults. Preserve omission locally; this alone does not prove server sparse-update behavior |
| Omitted amount-set column in a submitted options row | Block before approval: importer consumes all ten elements | Block; recover exact retained tuple or explicit approved changes, never clone another record |
| No optional child row | Do not manufacture unrelated rows to satisfy a template inventory | Do not clone or synthesize unrequested existing rows |

For updates, obtain retained values through the already selected workflow before
packaging when the importer needs a complete structure. A create/update label
is intent, not proof of target existence; existence and generic sparse-update
semantics remain disclosed target checks. Unknown required context is a precise
input finding, distinct from a nonblocking unsupported reference lookup.

## Observed Optional UI Defaults

The 2026-10-14 unsaved create-page inspection corroborates these visible defaults
for the ordinary PROJECT_PLAN/COST_ONLY branch. These are preparation choices
for a new type, not newly discovered mandatory importer fields. Explicit choices
win. Never apply new-row initialization to updates or treat a blank template as
its authority. The buffer row also states the separate conditional save rule,
which applies to submitted create/update options as detailed below.
The inspection was target- and identity-specific, discarded without saving,
and does not establish other releases' feature state or configured references.
Historical UI and import test records are developer evidence, not runtime
prerequisites; the rules and their limits are stated here and in their owning
validation, lookup and design resources.

| CSV scope | Attribute | Observed create value | Conditions and limits |
|---|---|---|---|
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | TimePhasedCode | N | None; explicit G/P activates period-based planning |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | NtpRateDateType | START_DATE_PRJ_PLAN | Cost-row start date; G/P permits this or EFFECTIVE_RATE_DATE only |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PercentCompCalcMethod | MANUAL | Cost method requires costs enabled; output-units feature remains separately checked |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | EtcMethodCode | MANUAL | Remaining plan is an explicit supported override |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | PercentCompRollupMethod | COST, displayed disabled with costs off | Preserve inactive initialization; never describe it as enabled cost rollup or require costs solely to serialize this retained default |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | AutoPlanAsmtFlag; MapActSummaryFlag; ManualSpreadFlag | N | Observed unchecked controls; manual spread is active only for G/P |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | Name (period profile) | Accounting Period for G; Project Accounting Period for P | UI defaults on calendar change, not a universal target reference. Materialize only when the local reference policy applies; follow resolve_period_profile for target-validation status and disclose unresolved membership. Do not assign a profile for N |
| PJO_PPT_PLAN_OPTION_RATE_SCH.csv | UsePlanningRatesFlag | N | Only a requested new BU rate row; do not create a row automatically. Each row has its own mode |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | Name2; Name3 | Empty, inactive until corresponding generation enabled | No budget/forecast type default; obtain the selected type name when enabling generation |
| PJO_PPT_PLAN_OPTION_GEN_OPT.csv | SyncTxnDateBuffer | Empty before Save; 0 on Save when synchronization is Y | Optional business input. After merging the request and baseline, materialize 0 only for an empty active buffer; preserve supplied integers and retained nonempty values |

Currency settings displayed Use same conversion attribute for all currency
conversions selected, with blank Rate Type and Date Type. The checkbox is a
transient UI action, not an exported flag. Its source-backed persistent-field
mapping is in Design Enforcement under Conversion Copy. Do not infer a rate
type, date basis, date or exchange rate from the checked display state.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PJO.PPT.DEFAULTS | step | 5 | apply_default | defaulted-or-preserved->PJO.PPT.VALIDATE_INPUT;unresolved->PJO.PPT.INPUT_ISSUES | none | stop | Apply documented create defaults and the conditional active-buffer save default on submitted create/update options; otherwise preserve supplied/current values and continue |

## UI Behavior Boundaries

The synchronization buffer has a conditional save-time rule, separate from
new-record defaults: when the submitted options row has SyncTaskTxnPlanDates=Y
and its effective buffer is empty, prepare SyncTxnDateBuffer=0. An explicit
integer (positive, zero or negative) wins over any retained value; an omitted
buffer retains a nonempty baseline value. An explicit empty active buffer
therefore becomes 0. With synchronization N, preserve the inactive buffer.
Do not add an omitted options row to an unrelated parent-only update. Apply the
same rule to a submitted duplicate's effective options after source merging.
Disclose each applied zero as conditional_save_default in defaultsApplied,
including before/after values and reason, and include it in the Task Hook preview.
The validator checks these prepared bytes without mutating them; a blank active
buffer returns UNMATERIALIZED_DEFAULT, not a request for extra business input.

Duplicate has a separate source-backed policy: reset StartDate to 1957/01/01,
clear EndDate, reset DefaultFinPlanTypeFlag and initialize DefaultAwdFinPlanTypeFlag
to N unless explicitly overridden. Preserve copied configuration, with only the
documented source-null fallbacks listed in scripts/README.md. Do not replay
general create defaults over a source copy. Renames and retained-row updates
apply no create defaults; the conditional active-buffer save rule still applies
to submitted options rows. Explicit child insertion defaults only a new BU mode
to N. Disclose every default separately from derived copy/rename/insert changes.

Default materialization is separate from activating a control. Preparation checks
explicit create choices and changed update values against the effective state.
In particular, the inactive COST rollup default is retained with costs off;
explicitly requesting active cost rollup requires compatible cost/revenue state.
Negative ETC remains selectable with Manual entry; its calculation effect is
distinct from its setup value. Automatic forecast approval requires generation.
Never silently change prerequisite choices to make
an otherwise incompatible request pass. See the design rules and UI coverage
record for control applicability and outstanding acceptance evidence.

Project-plan and financial-plan editors expose different controls. Hidden class or amount choices do not mean their values are cleared. Do not apply financial-plan-only interactions to this task.

Enabling multicurrency applies the UI change immediately. Disabling previously enabled multicurrency opens a warning; No restores the previous enabled setting. Save and Cancel retain their normal save/discard boundaries. The task importer deletes all retained currency rows when the parent changes from Y to N. This indirect deletion is excluded: preparation blocks that transition when the fresh baseline contains currency rows. A safe parent flag change propagates to exact retained options rows without applying create defaults. Do not invent rate-clearing behavior; dialog dismissal is not approval.

The UI initializes a new plan type's start date from database time, but that does not establish the import default. FSCR uses the narrower omitted-date-only policy above: preserve an explicit date and use the confirmed target business date only when omitted. Disclose both original and resulting working input.
