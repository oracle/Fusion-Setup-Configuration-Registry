# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Classify the plan type | Apply the PROJECT_PLAN setup context and evidenced parent/child planning scope; a shared FINANCIAL_PLAN control does not establish applicability. |
| 2 | Enforce editability | Do not change fields that the source makes read-only for attached or seed data. |
| 3 | Preserve route boundary | Use the supported task-level FSM export/import route; preserve the current export package schema through validation, preview, approval, and submission. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| planTypeCode is PROJECT_PLAN | Blocker | resolve_plan_class | Requested class or hidden option lacks task-route applicability | Preserve evidenced existing structure; obtain task-specific evidence before new non-default combinations | No |
| A plan type is attached or seed data | Blocker | resolve_existing_plan_type | Current evidence marks the requested field protected | Do not alter the protected value through this route | No |
| Third-party scheduling is enabled at PLAN_TYPE | Blocker | | A requested activation targets EnableRevForProjPlan, MapActSummaryFlag, RaTaskDatesSame or AutoRollupTaskDate | Preserve inactive values. Cost planning, calendar, progress, automatic planned assignments and transaction-date synchronization remain configurable; do not apply PLAN_VERSION restrictions | No |
| Currency or Rate Settings are requested | Blocker | | Both EnableCostsForProjPlan and EnableRevForProjPlan are N | Preserve disabled settings; use effective cost-row flags. Third-party scheduling alone does not disable these tabs at PLAN_TYPE. Unknown eligibility is disclosed as unresolved/nonblocking | No |
| Duplicate | Blocker | resolve_existing_plan_type | The exact name already exists for the selected plan-type branch | Choose a distinct name or explicitly update the eligible existing row | Yes |
| Duplicate source | Blocker | resolve_existing_plan_type | Source is ambiguous, has an unsupported branch or BudgetaryControlsFlag Y with unmapped XCC children | Retain the exact source; never silently make a partial copy | No |
| Rename | Blocker | resolve_existing_plan_type | Selected translation identity is missing, new name collides, or rename is mixed with another change | Preserve old parent key, update selected retained language rows and verify the new identity by fresh export | No |
| Insert a child on update | Blocker | | New set/BU/currency/language identity already exists, duplicates another requested identity, or references a different parent | Use explicit insertRows for absent identities and rows for retained identities; never infer deletion from omission | No |
| Delete, including a child assignment | Blocker | | Always excluded from this skill | Preserve the row; do not select an alternate deletion route | No |
| Multicurrency changes from Y to N | Blocker | | Fresh baseline contains currency rows for the selected type; the importer would delete them | Preserve multicurrency; report DESTRUCTIVE_CURRENCY_RESET_EXCLUDED | No |
| Requested revenue activation | Blocker | | EnableRevForProjPlan=Y without EnableCostsForProjPlan=Y | Obtain an explicit compatible cost-planning choice; do not enable it silently | No |
| Requested revenue calculation method | Blocker | resolve_rev_classification | Revenue planning is not enabled | Resolve revenue enablement first | No |
| Requested automatic planned assignments or summary-task actual association | Blocker | | Both AutoPlanAsmtFlag and MapActSummaryFlag would be Y | Resolve the conflicting choice; preserve unchanged inactive values | No |
| Requested manual spread activation | Blocker | resolve_calendar | ManualSpreadFlag=Y with TimePhasedCode outside G/P | Select a periodic calendar or leave manual spread inactive | No |
| Requested automatic forecast approval | Blocker | | ProgAutoApprFcstVer=Y without ProgAutoGenFcstVer=Y | Resolve generation and its selected forecast type first | No |
| Requested BU schedule change | Blocker | | Requested person, job, nonlabor or burden schedule with BU UsePlanningRatesFlag other than Y, or bill schedule without enabled revenue | Resolve effective BU mode and cost/revenue context; retain unchanged inactive schedules and supported actual-rate fallbacks | No |
| Unmapped or UI-only option requested | Blocker | | No exported column or supported PROJECT_PLAN mapping is proven | Apply the input mismatch gate; do not invent a column or reuse a superficially similar flag | No |
| Dynamic reference or feature check has no supported validation route | Warning | | None solely because validation support is missing | Apply Unresolved Validation Policy; preserve supplied CSV representation and disclose unverified checks | No invented values |
| A direct API, UI write, or invented template contract is requested | Blocker | resolve_task_level_fsm_route | The request bypasses the current task FSM package or changes its schema without proof | Use the target-exported ZIP contract and Data Loader approval path | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_existing_plan_type | Existing-record or duplicate evaluation | Current identity, protection and duplicate state | ora_reference_lookups.md |
| resolve_plan_class | PROJECT_PLAN class applicability | Canonical class and supported task context | ora_reference_lookups.md |
| resolve_rev_classification | Requested revenue calculation method | Canonical method and revenue enablement context | ora_reference_lookups.md |
| resolve_calendar | Requested manual periodic spread | Effective canonical calendar code | ora_reference_lookups.md |
| resolve_task_level_fsm_route | Package generation and import | ProcessId, completed package contract, members, metadata, and checksum | ora_reference_lookups.md |

## Requested Changes and Retained State

Evaluate the effective merged row and the requested delta together. On create,
explicit inputs are requests; initialization defaults can remain inactive. On
update, an unchanged retained value is not a new activation. Do not clear it or
reject it solely because its control is disabled. A changed value targeting a
known disabled control is blocked. Preparation enforces these distinctions;
byte-only validation and caller-supplied narrative results cannot establish them.

Authoring sources: Oracle's [26D Create Project Plan Types](https://docs.oracle.com/en/cloud/saas/project-management/26d/oapfm/create-project-plan-types.html),
and ADE FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64 PlanningOption.jsff, including
ProgAutoGenFcstVer conditions at lines 3484, 3519 and 3540 (checked 2026-10-15).
These sources establish control relationships, not live importer acceptance.

The 2026-10-15 unsaved UI inspection shows Allow negative ETC calculation
enabled with ETC Method Manual entry. Accept and preserve this flag; do not
force Remaining plan. Its Remaining plan calculation effect is distinct from
whether the setup checkbox is selectable.

## Conversion Copy

`Use same conversion attribute for all currency conversions` binds to transient
`sameAttrSelected`; `handleCopyPcToPfc` invokes the model's `copyPcToPfc` action.
It has no CSV flag. For explicit shared-attribute intent, preparation accepts
`copyConversionAttributes: true` in its internal normalized request. Omit it
for independently configured attributes. Do not serialize a guessed boolean.
When source-form input supplies `Curr_Set_Use_Conversion`, retain it in
`sourceInput`. Preparation maps explicit true to the action, rejects an
explicit contradictory action and preserves independent conversion choices
for false/unspecified intent. The preview checks the resulting persistent
destinations against `finalData.sourceInput`; equal Pc/Pfc values alone do
not establish that RateSch attributes were copied. Include every derived
change even when a visible checkbox has no stored Boolean representation.

For the supported COST_ONLY project-plan PLAN_TYPE options row:

| Parent multicurrency | Source | Persistent destinations |
|---|---|---|
| Y | PcCost and PcRev RateType, RateDateType, RateDate independently | Corresponding Pfc and RateSch attributes; SpecPcCost/RevAtProjLevel also copy to SpecPfcCost/RevAtProjLevel |
| N | PfcCost and PfcRev RateType, RateDateType, RateDate independently | Corresponding RateSch attributes; inactive Pc attributes remain retained |

Require costs enabled and resolved source cost rate type/date basis. Preserve
explicit source values, validate fixed dates normally, and block explicitly
conflicting destination values. Do not apply PLAN_VERSION's cost-to-revenue
copy behavior to PLAN_TYPE. The preview must include every resulting field
change from `derivedChanges`, including propagated multicurrency flags.

Full-source authoring evidence, read 2026-10-15 at ADE label
`FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64_261014.0600.S`, under
`fusionapps/prj/components/projectsFinancials/control/financialPlanOptions/`:
`publicUi/public_html/oracle/apps/projects/control/financialPlanOptions/publicUi/page/PlanningOption.jsff`,
`publicUi/src/oracle/apps/projects/control/financialPlanOptions/publicUi/bean/PlanningOptionBean.java`,
`publicUi/adfmsrc/oracle/apps/projects/control/financialPlanOptions/publicUi/page/PlanningOptionPageDef.xml`, and
`protectedUiModel/src/oracle/apps/projects/control/financialPlanOptions/protectedUiModel/applicationModule/PlanTypePlanOptionAMImpl.java`,
method `copyPcToPfc`.
`protectedModel/src/oracle/apps/projects/control/financialPlanOptions/PlanTypeService/applicationModule/ProjectPlanTypeServiceAMImpl.java`
lines 235–445 establish the parent multicurrency propagation and currency-row
deletion during import. Source behavior establishes the transformation;
deployed-target import acceptance still requires independent readback.

## Non-delete Maintenance Contract

All operations retain the same task-level FSM/Task Hook/Data Loader route.
The helper's action syntax and preview provenance are in scripts/README.md.

| Operation | Import representation | Preservation and verification |
|---|---|---|
| Insert new set, BU-rate, currency or translation | Existing parent plus explicitly absent child identities in insertRows | Use current alternate keys and linked options rows; preserve omitted children. A new row is distinct from a retained-row patch. Validate new-row requiredness and context before approval |
| Rename in selected application languages | Old parent Name for NameAltKey resolution; retained PlanTypeTranslation child Name becomes the requested name | Translation identity remains PlanTypeId/Language and SourceLang remains retained. Verify requested language names after import; re-export before subsequent maintenance |
| Duplicate | Create under absent new Name with unique source parent/options and selected re-keyed children | Apply only documented duplicate resets/fallbacks, preserve source and logical DFF attribute positions, require explicit new translated names, block unmapped XCC state |

Oracle [26D setup data update rules](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/key-information-about-setup-data-export-and-import-processes.html)
establish create-if-absent, update-if-present and preservation of omitted records.
The task-specific multicurrency deletion exception remains blocked separately.

Additional full-source evidence at the same 261014.0600.S label, all beneath the
financialPlanOptions directory above:

- `protectedModel/src/oracle/apps/projects/control/financialPlanOptions/PlanTypeService/view/PlanTypeVO.xml`:
  NameAltKey and PlanTypeTranslation accessor; the linked translation VO and
  `view/link/PlanTypeVOToPlanTypeTranslationVO.xml` join through PlanTypeId.
- `protectedModel/src/oracle/apps/projects/control/financialPlanOptions/PlanTypeService/view/PlanTypeTranslationVO.xml`
  and `protectedModel/src/oracle/apps/projects/control/financialPlanOptions/protectedModel/entity/PlanTypeTranslationEO.xml`:
  writable Name; immutable PlanTypeId/Language key; required Name/SourceLang.
  These establish the rename representation without changing the parent key.
- `protectedModel/src/oracle/apps/projects/control/financialPlanOptions/protectedModel/entity/PlanTypeEOImpl.java`,
  `duplicate`, lines 271–397: parent resets, options and set assignments.
  The parent Attribute1–Attribute20 setters contain a source indexing anomaly;
  FSCR preserves the requested logical attribute names instead.
- `protectedUiModel/src/oracle/apps/projects/control/financialPlanOptions/protectedUiModel/applicationModule/PlanTypePlanOptionAMImpl.java`,
  `duplicatePlanType`, lines 3741–3805: new Name and per-BU rate copying.
- `protectedModel/src/oracle/apps/projects/control/financialPlanOptions/protectedModel/entity/PlanningOptionEOImpl.java`,
  `duplicatePlOptions`, lines 7352–7995: copied setup values, scoped null fallbacks
  and transaction currency children. Hidden Excel/XCC objects do not establish
  additional visible task controls; requested unmapped content must be disclosed.

This evidence establishes package construction, not deployment certification.
Target identity, privilege/editability checks, approval, process logs and fresh
export readback remain required for each live execution. Source evidence and
offline regression success must never be reported as an actual successful load.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PJO.PPT.DESIGN_GATE | step | 30 | design_enforcement | pass->PJO.PPT.EXECUTION_GATE;blocked->PJO.PPT.DESIGN_ISSUES | PJO.PPT.READINESS | stop | Local resolution completed, and any required live resolver completed, on the incoming graph branch |
