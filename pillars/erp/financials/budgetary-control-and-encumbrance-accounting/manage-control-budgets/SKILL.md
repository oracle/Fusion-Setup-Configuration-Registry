---
skill_id: "erp.financials.budgetary-control-and-encumbrance-accounting.manage-control-budgets"
name: "Manage Control Budgets Setup Task Guidance"
description: "Provides Manage Control Budgets setup guidance, including Supplemental, Revenue Funding, and Override rules, under Budgetary Control and Encumbrance Accounting."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Budgetary Control and Encumbrance Accounting"
functional_area_code: "ORA_XCC_PUBLICSECTOR"
task_code: "ORA_XCC_MANAGE_CONTROL_BUDGETS"
task_name: "Manage Control Budgets"
parent_skill_id: "erp.financials.budgetary-control-and-encumbrance-accounting"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.3.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "supplemental_rules"
  - "revenue_funding_rules"
  - "override_rules"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.rest-api-client"
  - "core.auth.fusion-oauth-authentication"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-control-budgets/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-control-budgets/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Writes project planning, validation, artifact/run and token-usage records through the declared project services."
  - "Delegates same-task template and requested readback exports to shared.setup-export.task-level-export."
  - "Delegates declared Fusion/HCM REST and read-only BOSS metadata lookups to core.fusion-api.rest-api-client and its OAuth service; that service may refresh its approved external token cache."
  - "Delegates approved FSM setup-data imports to core.data-loader; the loader owns immutable preview, approval, submission and process monitoring."
required_privileges:
  - "Access to the selected project and authorized Fusion target, task export/import privileges, and read privileges for the applicable Fusion, HCM worker/account and BOSS metadata resolvers."
---

# Manage Control Budgets Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Control Budgets` under `Budgetary Control and Encumbrance Accounting`.

## Setup Task Skill Contract

- task_code: `ORA_XCC_MANAGE_CONTROL_BUDGETS`
- task_name: `Manage Control Budgets`
- parent_skill_id: `erp.financials.budgetary-control-and-encumbrance-accounting`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Budgetary Control and Encumbrance Accounting`
- functional_area_code: `ORA_XCC_PUBLICSECTOR`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Control Budgets` under `Budgetary Control and Encumbrance Accounting`.

## Setup Task Metadata

- Task name: `Manage Control Budgets`
- Task code: `ORA_XCC_MANAGE_CONTROL_BUDGETS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export the setup-task CSV template/spec package with `shared.setup-export.task-level-export` using template mode. Use the template-export contract in `ora-resource/ora_reference_lookups.md`; do not require a ledger-scoped data export as package evidence.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
   When the user selects a tree for a budget segment, resolve its technical `TreeCode` from the same current-target COA segment result used for `SourceSegmentColumnName`, following `ora-resource/ora_reference_lookups.md`. A segment without a selected tree needs no tree-code resolution. Stop before ZIP generation if a selected tree has no unique exact match.
4. Import setup task data with `core.data-loader`.

Use `core.fusion-api.rest-api-client` for the declared reference resolutions in
`ora-resource/ora_reference_lookups.md`: its standard Fusion route covers
`/fscmRestApi` and `/hcmRestApi`, and its BOSS route covers `/api/boss`, including
the read-only COA detail action. Read the selected client's instructions before
invocation. Authentication and approved external token-cache handling belong to
`core.auth.fusion-oauth-authentication`; do not implement transport, login or
token storage in this pillar. These lookups run only at the selected task
workflow's lookup step after its input, target and privilege checks, not as
exploratory calls. Preserve existing exact-match, default and import-deferred
boundaries. The Core Data Loader workflow remains the only import route and owns
its approval gate; a task plan or successful lookup is not import approval.

### Control Budget and independent rule-group validation before package generation

Treat one request as a Control Budget phase followed by independent Supplemental, Revenue Funding, and Override Rule groups across every requested control budget. A request with only one group enters that group directly after the budget gate. Collect all independently checkable findings in every requested group before the final package gate, even when another group fails. Enumerate the budgets in prompt order from the normalized request and give the task-specific pre-ZIP validator Check outcomes derived from that request and current-target lookup evidence. The `ora-resource/ora_rule_registry.json` Task Hook plan remains a required package check, but its ordering alone does not enforce this request-wide boundary.

1. **Control Budget phase:** For every requested budget, validate its complete header, all budget segments, and every tree assignment and supplied tree-version row. Collect every independently checkable input, lookup, default, and design finding for every budget before the request-wide gate decision, even when an earlier budget fails. Use separate checks and prerequisite IDs for each segment and its tree: an unresolved segment skips only its own dependent tree check, while a selected tree on a different resolved segment is still checked. Keep the existing 1-to-30 segment-count check before lookup or template export for each budget; when it fails, still report other direct-input findings and mark lookup-dependent checks `not_evaluated` with their missing prerequisite. If any budget fails, return one combined report and do not validate any Supplemental, Revenue Funding, or Override Rule in the request.
2. **Supplemental Rule phase:** Only after every requested Control Budget passes, validate all supplied rules in budget and rule request order. For each rule, check its header, Budget Segment Filters, Additional Segment Filters, and Transaction Attribute Filters. Evaluate every independently checkable selection and every supplied Specific value, including all values in a single filter and all requested rules, before deciding whether the phase passes. A failed prerequisite skips only its dependent checks; record those as `not_evaluated` with the prerequisite, then continue independent checks in this phase.

3. **Revenue Funding Rule group:** Only after every requested Control Budget passes, validate every supplied Revenue rule's `rule_header`, `funding_targets`, and `revenue_source_segments` sections. Run the local `scripts/prepare_revenue_rules.py` check producer after the declared reference resolutions; merge its per-rule check outcomes into `revenueFundingRules` for the request-wide validator. A failed Supplemental Rule does not suppress this group. Enforce the user-confirmed eligibility, positive amounts, explicit limit choices, required scenarios, exact percentage total, COA-role selections, full source-segment coverage, and CSV mappings in the task resources. Supplied Specific value membership is deferred to Fusion import and must not block ZIP generation. Missing Specific values remain local input errors.

4. **Override Rule group:** Only after every requested Control Budget passes, validate every supplied Override rule's `rule_header`, `transaction_types`, `journal_conditions`, and `user_assignments` sections. Run `scripts/prepare_override_rules.py` after the declared Override Type and Transaction Type lookups and merge its per-rule checks into `overrideRules`. Supplemental or Revenue failures do not suppress this group. Support only effective `FvTypeCode=ORA_CONSUMPTION` with overrides enabled. Name, Override Type, Transaction Type selection, and at least one nonblank user assignment are mandatory for every rule. Apply conditional amount checks and the source-compatible amount-limit comparison in the Override resources. Journal source/category and username values are copied unchanged; their membership, exclusions, identity, and duplicate-assignment business validation are deferred to Fusion import. Structural selection consistency and mandatory assignment presence remain local checks.

Enumerate each segment/filter check and its dependent checks before recording outcomes. For each failed Detail/Master source-segment resolution, include `SourceSegmentColumnName is resolved and KeySegmentColumnName follows the display sequence` for that same segment as `not_evaluated`, with the failed resolution check's `id` in `prerequisites`. For each failed `Budget versus additional segment membership` check in Additional Segment Filters, include `Additional segment filter identity` for that same filter as `not_evaluated`, linked to the failed membership check. Legal Additional-segment membership is a prerequisite of that filter identity check, including when a resolved segment is already a budget segment. These skipped checks remain in the validation input and the helper's `actualIssues`; do not drop them when copying the terminal result. Use field paths on the same segment/filter object (or the same named-selector path) so dependencies cannot be satisfied by another input. `validate_units.py` rejects omissions of these specific dependent checks; repair the input report and run the helper again before returning the terminal result. Preserve the independent failures and their evidence.

For Summary source segments, distinguish COA resolution from membership in the linked Master. A successfully resolved segment absent from the Master fails exactly `Summary control-budget source segments are a subset of the linked master/detail source segments`. A missing/ambiguous COA match or supplied-column mismatch retains the Summary COA-resolution Check as its failure and marks the subset check `not_evaluated`. Apply the detailed ownership rules in `ora_input_validation.md`; do not alias all Summary resolution failures to the subset reason.

Persist one validation result for the active phase containing each issue's control budget, rule when applicable, field or filter path, supplied value when applicable, failed Check, failure class, sanitized lookup evidence, and recommended correction. Distinguish `failed`, `passed`, `not_evaluated`, and documented `deferred_to_fusion` checks. Preserve all existing named Checks, resolver identifiers, lookup matching rules, defaults, and single-error terminal reasons. `actualReason` remains one deterministic primary reason derived from the first failed Check: use budget request order then header, budget-segment, and tree order in the Control Budget phase; use budget and rule request order then rule-header, Budget Segment Filter, Additional Segment Filter, and Transaction Attribute Filter order in the Supplemental Rule phase. The issue list carries every independently detectable error. A resolver name is not substituted for a more specific Check. Do not generate a candidate ZIP, preview, or import while any requested group has a required failure; every Control Budget must pass before any rule group starts. For combined requests, select the first Supplemental failure in existing order, then the first Revenue failure, then the first Override failure in budget/rule/header/transaction/journal/user order; report all findings. A request without any rule group ends after the Control Budget phase and the usual package-readiness checks. Target validations already assigned to Fusion import remain deferred rather than being presented as pre-import passes. Keep nonblocking warnings separate from `actualIssues`; Allow Overrides enabled without rules is a warning, not a package blocker.

The Child must perform the semantic Checks in these task resources against the actual prompt, normalized request, and authorized current-target evidence. It must evaluate each applicable header, segment, tree, rule, filter, and each locally validated Specific value, then supply those outcomes to `scripts/validate_units.py` before candidate ZIP creation. For a request with multiple budgets, persist one sanitized JSON input with a nonempty `controlBudgets` array in prompt order. Each entry contains `controlBudget`, `controlBudgetChecks`, and optional `supplementalRules`, `revenueFundingRules`, and `overrideRules` for that budget; do not supply the singular fields at the top level or run the helper separately per budget. The legacy top-level fields remain valid for one budget. Include explicit section coverage even when a section has no selected items. Budget sections are `header`, `budget_segments`, and `segment_trees`. Supplemental sections are `rule_header`, `budget_segment_filters`, `additional_segment_filters`, and `transaction_attribute_filters`. Revenue sections are `rule_header`, `funding_targets`, and `revenue_source_segments`. Override sections are `rule_header`, `transaction_types`, `journal_conditions`, and `user_assignments`. Every rule contains `ruleName` and `checks`. An empty optional group is not applicable; omitting Revenue or Override arrays preserves existing report behavior. Every check has `id`, `section`, `path`, `check`, and `status`; a failed check includes an `issues` entry for each invalid supplied value. A prerequisite-dependent check uses `not_evaluated` and names its prerequisite; a Fusion-deferred check uses `deferred_to_fusion`, a documented `basis`, and an allowed `deferralId`. Override-only deferrals are `journal_source_membership`, `journal_category_membership`, and `override_user_membership`; they do not relax Supplemental Transaction Attribute validation. Transaction Attribute type and Specific value lookups cannot be deferred; failures under those Checks must retain sanitized lookup `evidence`. Do not assert `passed` for an unevaluated check or use one catch-all pass for an entire section. The helper verifies outcome structure, section coverage, allowed deferrals, dependencies, aggregation, and gate order; it does not read the prompt, perform lookups, or prove every requested input has an outcome.

The Child must explicitly run `python pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-control-budgets/scripts/validate_units.py --input <sanitized-checks.json> --output <validation-report.json>` once for the complete request before ZIP generation; Data Loader and its Task Hook do not invoke this helper automatically. Inspect and persist the single report. For multiple budgets, copy each finding's `controlBudgetName` and one-based `controlBudgetIndex` into the test-suite Child issue and show the budget name beside every finding in the user-facing response. Continue to ZIP generation only when the script exits successfully and the report has `status=passed` and `packageReady=true`. On exit code 2, return its combined `actualIssues` and `actualReason` without ZIP generation. The helper's `actualReason` is a string such as `task_rule:Transaction attribute values`; when reporting a test-suite Child result, map it to the required reason object, for example `{"source":"task_rule","code":"Transaction attribute values"}`. Do not copy the suite's expected reason or derive a reason from prose. A contract error must be corrected and rerun before preparation; it is not a passing validation result. This Child-invoked gate supplements the ordered Task Hook resource results and does not replace the shared template, preview, approval, or import steps.

### Exact numeric preparation inputs

Retain user-entered financial numbers as decimal strings in normalized requests
before any binary floating-point conversion. The Revenue and Override preparation
CLIs also preserve the original fractional/exponent tokens of JSON numbers,
including trailing zeros, while keeping numeric tokens distinct from text fields.
Their programmatic interfaces accept decimal strings, integers, and `Decimal`
values; they reject binary `float` amounts and percentages because earlier
rounding or lost decimal text cannot be recovered. Never repair such a value by
stringifying an already rounded float; normalize again from the original input.
Exact numeric comparisons do not rewrite the supplied CSV representation.

### Revenue Funding Rules

When Revenue Funding Rules are requested, use the same reviewed Manage Control Budgets FSM package as the parent budget and any requested Supplemental Rules. Load the Revenue sections of all six ora-resource files. The final user-approved eligibility is only header `AllowRevenueFundingFlag=Y` and Source Budget Type `Other`, resolved by the existing source-budget-system resolver. Do not add Procure to Pay, ledger-currency matching, or an assigned Budget Chart of Accounts as Revenue eligibility blockers, and do not alter existing header validation or defaults for requests without Revenue rules.

Both limit types are explicit business inputs resolved independently through `ORA_XCC_REVENUE_LIMIT_TYPE`; never default them or hardcode observed codes. Fixed amounts must be finite numeric values greater than zero. Revenue estimate requires a nonblank scenario; both limits cannot use Revenue estimate. Preserve optional description text. Require target accounts and positive percentages totaling exactly 100 using decimal arithmetic. Target combinations use the parent's ordered budget segment count. Every Revenue source includes all of its source ledger's COA segments, with returned `segmentColumnName` condition codes. Identify the mandatory Specific segments directly from exact `GL_BALANCING` and `GL_ACCOUNT` tokens in `segmentLabels` in the current selected-source COA BOSS response; no additional metadata join or artifact is required. Each role requires at least one user-supplied value. Other segments default to All; an explicit Specific selection also requires a value. Do not infer business values, segment roles, source columns, or codes.

Run `python pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-control-budgets/scripts/prepare_revenue_rules.py --input <normalized-revenue-request.json> --output <revenue-preparation.json>` after the Control Budget gate and declared lookups. Its normalized input is one `controlBudget` with `name`, resolved `sourceBudgetType`, `allowRevenueFundingFlag`, and ordered `budgetSegments`, plus `revenueFundingRules`. Each rule supplies `ruleName`, optional `description` and `enabledFlag`, `maximumFunding` and `minimumRevenue` objects with `type`, resolved `lookupCode`, and applicable `amount` or `budgetScenario`; `fundingTargets` contains `budgetAccount` and `fundingPercentage`; `revenueSource` contains resolved `ledgerName`, `coaSegments` with returned `segmentName`, `segmentColumnName`, `segmentLabels`, and `sequenceNumber`, and optional `segmentFilters` keyed by the resolved column with `selection` All/Specific and supplied `values`. Retain each authoritative `sequenceNumber` from the existing BOSS COA detail response; no additional lookup or metadata join is required. Labels may be a token array or the BOSS bracketed comma-separated token string; match whole tokens, never substrings. The helper performs no live lookup, export, ZIP generation, or import. Keep source-response provenance separate from CSV fields and bind it to the same source COA and request.

Validate Revenue source `sequenceNumber` using the metadata input contract in `ora_input_validation.md`; missing, invalid, or numerically duplicate sequences block ZIP generation, while gaps are allowed. Apply the source ordering in `ora_design_enforcement.md`: source Condition rows and Detail groups follow ascending numeric sequence, preserving returned codes, roles, and entered value order/leading zeros. All selections still produce no Details, rules retain request order, and target conditions/Details remain last in target request order. This ordering applies only to Revenue rows; existing Control Budget segment order and Supplemental mappings are unchanged.

Inspect all returned checks, merge the per-rule results into the single request's `validate_units.py` payload, and still run that request-wide helper once. Only use mapped `csvRows` when Revenue preparation exits 0 with `status=ready` and `packageReady=true`, and the final request-wide gate exits 0 with `status=passed` and `packageReady=true`. Preparation exits 1 for local rule blockers and 2 for malformed input or artifact persistence failure; preserve its checks/diagnostic and do not generate a ZIP. A request without Revenue rules adds no Revenue data rows and never copies business rows from a reference export. Match their member names and field order to the selected same-task template before writing CSV. Any rule failure prevents using partial mapped rows. Details preserve entered text and leading zeros. Membership of supplied source values, target budget accounts, and scenario names is validated by Fusion import; retain explicit deferral results rather than reporting those as local passes. Required inputs, local numeric/shape checks, lookup codes, role evidence, segment coverage, and parent links cannot be deferred.

Keep the existing immutable preview, Core Data Loader approval, import, polling, diagnostics, and readback route. This enhancement creates rule setup; it does not submit the Create Budget Entry from Revenue process.

### Override Rules

Load the Override sections of all six ora-resource files only when Override
rules are requested. Use the existing same-task FSM template, immutable preview,
Core Data Loader approval, import, diagnostics, and readback workflow. This adds
rule setup; it does not perform an override on a transaction or introduce BOSS
or UI writes. Cash control budgets (`ORA_CASH`) are outside this enhancement.

Collect the two budget-manager notification choices during the Control Budget
header phase. In `ORA_XCC_CONTROL_BUDGET.csv`, map "Notify budget manager when
no overrides are available" to `NoOverridesNotifyFlag` and "Notify budget manager
when overrides are taken" to `OverridesTakenNotifyFlag`. Map each choice
independently: enabled is Y, disabled is N, and omission defaults to N. Preserve
explicit choices for each budget; enabling overrides or enabling a rule does
not automatically enable either notification.

After the request-wide Control Budget gate passes, resolve Override Type through
`XCC_CB_OVERRIDE_TYPE_CODE` and Transaction Type through `XCC_TRANSACTION_TYPES`,
restricted to `GL_JOURNAL`, `INVOICE`, `PURCHASE_ORDER`, `REQUISITION`, and
`SLA_JOURNAL`. Keep exact code/meaning and current-target lookup evidence; never
infer a code from misspelled text. Source, category, and user-assignment values
have no lookup: retain them exactly for `JeSourceCode`, `JeCategoryCode`, and
`UserName`. Require at least one nonblank assigned user on every rule, including
disabled rules, but leave identity, eligibility, and duplicate-user validation
to import. Do not derive a username from a display name or assign a budget
manager automatically.

Run `python pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-control-budgets/scripts/prepare_override_rules.py --input <normalized-override-request.json> --output <override-preparation.json>`.
The offline helper accepts one `controlBudget` with `name`, `fvTypeCode`,
`allowOverridesFlag`, and optional `maximumOverrideAmount`, plus `overrideRules`.
Each rule supplies `ruleName`, optional `description`/`enabledFlag`,
`overrideType` with resolved `lookupCode` and optional `meaning`, conditional
`amount`, `transactionTypes` with explicit `selection` All/Specific and resolved
`values` for Specific, optional `journalSources`/`journalCategories` with
All/Specific selections and raw string `values`, and raw `userAssignments`.
The helper documents the precise normalized contract and performs no external
calls. It defaults an omitted new-rule enabled choice to Y and description to
empty; it does not supply missing business amounts, types, or assignments.

Insufficient Funds requires a finite positive rule amount; Closed Period has
no amount. A supplied header maximum is finite and nonnegative. Each enabled
Insufficient Funds rule with an amount requires a positive covering maximum.
Preserve the source's `BigDecimal.intValue()` semantics only for amount-limit
comparison; preserve the complete decimal amounts in CSV. Read the numeric
scope and source caveat in `ora_input_validation.md` before evaluating limits.

All transaction types sets all three applicability flags Y and creates no
transaction or journal child rows. A proper Specific transaction subset creates
linked rows; selecting all five supported types normalizes to All. Follow the selection matrix and preserve every supplied journal/user
value, including duplicates; reject contradictory All/Specific structure
instead of discarding user input. Specific sources with All categories use an
empty CSV `JeCategoryCode`, as evidenced by FSM exports, not the model's single
space. Require the four exact Override member headers and parent links from
`ora_reference_lookups.md`. A request without Override rules adds no Override
data rows and retains all unrelated template members.

Merge the returned `overrideRules` checks into the single request-wide
`validate_units.py` payload. Use `csvRows` only when preparation reports
`status=ready`, `packageReady=true`, and the final request-wide gate passes.
Persist all independently detectable findings and prerequisite-based
`not_evaluated` results. Retain the three declared import deferrals rather than
asserting value validity. Keep warnings outside blocking findings.

### Supplemental Rules

When a request includes Supplemental Rules, keep them in the same reviewed Manage Control Budgets FSM package as their parent control budget. A rule changes the control level or tolerance for matching transactions; it does not replace the control-budget header. Apply `ora-resource/ora_input_validation.md`, `ora-resource/ora_reference_lookups.md`, and `ora-resource/ora_dependency_readiness.md` to the rule, its conditions, and its detail values before package generation. The three task CSV members are `ORA_XCC_CONTROL_BUDGET_SUPPLEMENTAL_RULE.csv`, `ORA_XCC_CONTROL_BUDGET_SUPPLEMENTAL_RULE_CONDITION.csv`, and `ORA_XCC_CONTROL_BUDGET_SUPPLEMENTAL_RULE_DETAIL.csv`; use only the headers and member paths from the current same-task template export.

Require a rule name and control level, and resolve the control level through the existing `resolve_control_level_code` lookup. Business Unit is optional and belongs to the Supplemental Rule header: copy the supplied Business Unit name unchanged into `ORA_XCC_CONTROL_BUDGET_SUPPLEMENTAL_RULE.csv` `Name`, or write `""` when omitted. Keep `RuleName` separate, and use the same `Name` value in linked condition and Detail parent columns. Do not serialize Business Unit as a condition or Detail value. A new rule is enabled by default: write `EnabledFlag=Y` when the user gives no enabled choice, and `N` only when the user explicitly disables it. For each supplied rule, create one Control Budget Segment Filter condition for every segment of its parent control budget, in the same `DisplaySequenceNumber` order as the header's segment rows. The first segment uses `FilterConditionCode=SEGMENT_VALUE1`, the second `SEGMENT_VALUE2`, and so on; each uses `FilterConditionType=BUDGET_GL_COA_SEGMENT`. If the user supplies no value selection for a segment, use All values (`ApplicableToAllValuesFlag=Y`) and no detail rows. Specific values use `N` and matching detail rows. Do not omit a parent segment or reorder these conditions.

Supplemental Rule `Description` is optional: copy supplied text unchanged to the header `Description` column, or serialize `""` when omitted. Do not derive it from `RuleName` or Business Unit.

Write user-supplied specific control-budget segment filter values as `FilterConditionValue` Detail rows after local shape, duplicate, and relationship checks. Fusion import validates whether those values exist for the target segment; a prior export or live value lookup is not required before package generation. Reject a requested Budget Segment Filter whose source segment is absent from the parent budget's ordered segment rows.

For Additional Segment Filters, resolve the effective ledger's chart of accounts and its current-target segment list. Allow only source segments in that chart of accounts that are not budget segments on the parent control budget. Use `FilterConditionType=GL_COA_SEGMENT` and the selected segment's returned `segmentColumnName` (such as `SEGMENT3`) as `FilterConditionCode`; never derive this code from the parent budget segment order or copy a mapping from another ledger. Use `TreeStructureCode=GL_ACCT_FLEX` for a selected tree and resolve its technical `TreeCode` against that same COA segment as described in `ora_reference_lookups.md`. A tree and its version are optional; an unselected tree needs no tree lookup. When the user supplies a tree version, copy its nonblank text unchanged into `TreeVersionName` and leave version existence and applicability to Fusion import, as for budget segment trees. Do not block package generation solely because a separate current-target tree-version lookup is unavailable. For both budget and additional segment filters, omitted values mean All values: write `ApplicableToAllValuesFlag=Y` and no Detail rows, even when an additional filter has a selected tree. Specific values mean `N` and linked Detail rows. Existing same-task exports show additional filters with specific values (`N`); the user-confirmed All default governs omitted values. Reject an additional segment that is already used by the budget, is absent from the effective ledger COA, or duplicates another condition. Preserve exact parent and condition links across the three CSVs.

For each supplied Supplemental Rule, discover its Transaction Attribute Filter types from the current target's `XCC_TRX_ATTRIBUTE_FILTER_CODES` lookup; do not hardcode the present five types. Create one `TRANSACTION_ATTRIBUTE` condition per returned enabled type in lookup display order, including types the user did not mention. Use that type's `LookupCode` unchanged as `FilterConditionCode`. Omitted values and explicit All mean `ApplicableToAllValuesFlag=Y` with no Detail rows. For types with specific values, validate each supplied display label or code against the type's declared current-target value source and write the matched technical code to Detail `FilterConditionValue`; use `ApplicableToAllValuesFlag=N`. For `NATURAL_ACCOUNT_TYPE`, validate every supplied specific value against the current-target BOSS `lookupLists` response filtered by `lookupType='ACCOUNT TYPE'` and `lookupCategoryId=101`, and write the uniquely matched nonblank `lookupCode` unchanged to Detail `FilterConditionValue`. Block ZIP generation if any value has no unique exact match or no nonblank `lookupCode`. An unknown type or unmatched, ambiguous, or unavailable specific value blocks ZIP generation. For a supplied Specific value that is invalid, unmatched, ambiguous, excluded, unavailable, or missing a required technical code, record `task_rule:Transaction attribute values` as the terminal reason, using the exact Check label in `ora_input_validation.md`. Report a failed transaction attribute type-set check, including an unknown supplied type or incomplete current-target type lookup, as `task_rule:Transaction attribute type set`, the exact Check label in `ora_input_validation.md`. Keep `resolve_supplemental_rule_package_contract` as the resolver identifier distinct from the terminal reason; use it as a terminal reason only for other condition or package-contract failures lacking a more specific Check. Derive the reason from the failed validation and preserve lookup evidence. Apply the type-specific lookup, processing-type, and CSV rules in `ora_reference_lookups.md` and `ora_input_validation.md`.

Resolve other requested condition categories, values, or optional tree fields only from authoritative current-target or same-task export evidence as described in `ora_reference_lookups.md`. If another requested condition has no declared, complete resolution path, stop before ZIP generation and report the missing evidence. A request with no Supplemental Rules retains the existing header-and-segment workflow plus any explicitly requested independent Revenue or Override group, and leaves Supplemental members without data rows.

The existing template export, Task Hook, immutable preview, approval, Data Loader import, and diagnostic route remains authoritative. Do not use a separate UI or REST write route for Supplemental Rules. Oracle distinguishes cash from procure-to-pay control budgets when supplemental rules affect a later **budget balance import**; this does not change the Manage Control Budgets setup-data import route.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Budgetary Control and Encumbrance Accounting`
- Setup task name: `Manage Control Budgets`
- Setup task code: `ORA_XCC_MANAGE_CONTROL_BUDGETS`




## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `supplemental_rules` (optional)
- `revenue_funding_rules` (optional)
- `override_rules` (optional)

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

### Developer Validation

Run the canonical offline tests through the task-local discovery entry point:

```text
python -B -m unittest discover -s pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-control-budgets/noship/tests -p test_*.py
```

All assertions, fixtures and harnesses remain in the functional-area
`noship/tests/manage-control-budgets/` folder. The task-local `noship/tests/`
entry point delegates to that canonical suite without copying assertions.
The [local controller guide](../noship/tests/manage-control-budgets/e2e/controller/README.md)
documents the optional developer E2E harness, which is not an implementation skill.
Exclude both `noship` trees from deployed bundles.

`scripts/validate_units.py` requires a new output path and preserves existing
files. Exit codes are 0 for a passed gate, 2 for task-rule blockers and 1 for
input-contract, output-conflict or persistence failures. Such failures emit a
sanitized structured diagnostic with `packageReady=false`; an input diagnostic
is also written to a new output when possible. Use the project artifact-version
workflow for any approved replacement. Check aggregation, reason ordering and
import approval gates remain authoritative.

Use the parent functional-area skill `erp.financials.budgetary-control-and-encumbrance-accounting` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
