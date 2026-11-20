# Manage Control Budgets Defaulting Rules

Apply a documented default after the package contract is verified by either target metadata or an approved cross-instance reference baseline. A user-supplied value overrides a default only when it is valid for the selected baseline.

Apply Control Budget header, budget-segment, and assigned-tree defaults for every requested budget in the first validation phase. Only after every budget passes its request-wide gate, apply Supplemental Rule header/filter, Revenue, and Override defaults to their respective requested groups independently. A failure in any group does not suppress another's default checks; the final package gate retains all three groups' findings. A default must not hide a malformed explicit selection or a failed lookup. Collect independent defaulting errors across the active group; mark a default requiring unresolved evidence `not_evaluated` and identify that prerequisite. Retain the defaults and CSV representations in the table below unchanged.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Description | Semantic NULL, serialized as CSV empty string (`""`) | Not supplied | No | resolve_fsm_package_metadata |
| SourceBudget | Control budget Name, serialized as CSV text | Detail control budget Source Budget Name is not supplied | No; preserve an explicitly supplied Source Budget Name unchanged | resolve_fsm_package_metadata |
| SourceBudget | Resolved master/detail control budget Name, serialized as CSV text | Summary Control Budget | No; require it to equal MasterCb and reject a conflict | resolve_master_control_budget_baseline |
| MasterCb | Resolved master/detail control budget Name, serialized as CSV text | Summary Control Budget | No; require it to equal SourceBudget and reject a conflict | resolve_master_control_budget_baseline |
| LedgerName, CurrencyCode, UserConversionType, ChartOfAccountsName | Corresponding resolved master/detail control-budget baseline values from the current export or explicitly requested atomic archive; apply the Default Rate Type contract in ora_input_validation.md before defaulting. When the final currency is STAT, UserConversionType is the actual empty string rather than a baseline value. | Summary Control Budget after applicable currency input resolution and the Summary consistency check | No for LedgerName, CurrencyCode, and ChartOfAccountsName. For STAT UserConversionType, replace any supplied or inherited rate with the actual empty string and retain the discarded value only as preview evidence. | resolve_master_control_budget_baseline |
| UserPeriodSetName, StartPeriodName, EndPeriodName | No default; preserve the Summary Control Budget calendar and period range supplied by the user | Summary Control Budget | No; require complete user input and defer target-period validation to Fusion import | defer_target_reference_validation_to_import |
| ChartOfAccountsName | Resolved chart-of-accounts StructureInstanceCode, serialized as CSV text | Detail control budget LedgerName supplied | No | resolve_chart_of_accounts_name |
| CurrencyCode | No guessed or literal default; use only the verified currency output | Detail currency input supplied | No; do not substitute ledger currency, a reference-example currency, the entered display name, or a blank value for required resolution | resolve_currency_code |
| BudgetMgrUserName | Semantic NULL, serialized as CSV empty string (`""`) | Not supplied | No | resolve_fsm_package_metadata |
| ToleranceAmount | Semantic NULL, serialized as CSV empty string (`""`) | Not supplied | No | resolve_fsm_package_metadata |
| TolerancePercent | Semantic NULL, serialized as CSV empty string (`""`) | Not supplied | No | resolve_fsm_package_metadata |
| UnitOfMeasure | Exact linked Master UnitOfMeasure code; a known blank non-STAT Master value serializes as CSV empty string ("") | Summary Control Budget after Master baseline, final currency, and Summary UOM contract validation | No; preserve the inherited code exactly and reject conflicting supplied Summary code instead of silently overwriting it | resolve_master_control_budget_baseline |
| UnitOfMeasure | Semantic NULL, serialized as CSV empty string ("") | Detail/Master value not supplied and final CurrencyCode is resolved and is not STAT, using trimmed case-insensitive comparison | No; never apply a blank default to STAT, replace Summary inheritance, or overwrite the result of resolve_unit_of_measure_code | resolve_fsm_package_metadata |
| ProjectId | -99 | Not supplied | No | resolve_fsm_package_metadata |
| AccountCreationAllowedFlag | N | Not supplied | No | resolve_fsm_package_metadata |
| BalanceIncreasesAllowedFlag | N | Not supplied | No | resolve_fsm_package_metadata |
| BalanceDecreasesAllowedFlag | N | Not supplied | No | resolve_fsm_package_metadata |
| NegativeBalancesAllowedFlag | N | Not supplied | No | resolve_fsm_package_metadata |
| AllowOverridesFlag | N | Not supplied | No | resolve_fsm_package_metadata |
| NoOverridesNotifyFlag | N | Notification choice omitted; explicit enabled maps to Y and disabled to N | No; preserve each explicit choice independently in ORA_XCC_CONTROL_BUDGET.csv | resolve_fsm_package_metadata |
| OverridesTakenNotifyFlag | N | Notification choice omitted; explicit enabled maps to Y and disabled to N | No; preserve each explicit choice independently in ORA_XCC_CONTROL_BUDGET.csv | resolve_fsm_package_metadata |
| MaximumOverrideAmount | Semantic NULL, serialized as CSV empty string (`""`) | Not supplied | No | resolve_fsm_package_metadata |
| UserConversionType | Actual empty string; do not invent a conversion rate type | Effective CurrencyCode is STAT using trimmed case-insensitive comparison; for Summary, apply its Master linkage first, then set the rate blank regardless of any supplied or inherited rate. | Yes; replace any supplied or inherited value with the actual empty string, while retaining the original value only as non-CSV preview evidence. | resolve_fsm_package_metadata |
| UserConversionType | No default; obtain the required user-supplied Detail/Master rate or the linked Master rate for Summary, as required by ora_input_validation.md | Final CurrencyCode is resolved and is not STAT, using trimmed case-insensitive comparison | No; never fill with a blank, ledger-derived, example, or unrelated prior-budget rate, or replace a missing Master rate with a Summary-only value | resolve_fsm_package_metadata |
| ProjectName | Semantic NULL, serialized as CSV empty string (`""`) | Not supplied | No | resolve_fsm_package_metadata |
| MasterCb | Semantic NULL, serialized as CSV empty string (`""`) | Detail control budget value not supplied | No | defer_target_reference_validation_to_import |
| FundsReleaseTimeframe | `RELEASE_IMMEDIATELY` | Master/Detail (non-Summary) Control Budget, whether the user supplies a value or not | Yes; replace a supplied value with the exact literal and retain the original only as non-CSV preview evidence. Do not run a lookup. | resolve_fsm_package_metadata |
| FundsReleaseTimeframe | `RELEASE_IMMEDIATELY` | Summary Control Budget and no value is supplied | No; an omitted Summary value does not trigger a lookup or inherit the Master value. | resolve_fsm_package_metadata |
| FundsReleaseTimeframe | Exact LookupCode returned by `ORA_XCC_CB_FUNDS_REL_TIMEFRAME` | Summary Control Budget and a value is supplied | Yes; replace the supplied display value with the returned LookupCode. Block no match, ambiguity, a blank code, or lookup failure. | resolve_funds_release_timeframe_code |
| FvTypeCode | ORA_CONSUMPTION | Not supplied | No | resolve_fsm_package_metadata |
| AllowRevenueFundingFlag | N | Not supplied | No | resolve_fsm_package_metadata |
| TransTreeStructureCode | GL_ACCT_FLEX | Not supplied for a segment | No | resolve_fsm_package_metadata |
| SourceSegmentType | GL_COA_SEGMENT | Not supplied for a segment | No | resolve_fsm_package_metadata |
| SourceSegmentColumnName | Exact `segmentColumnName` returned by `resolve_source_segment_column_name` for the effective ledger and SourceSegmentName; for Summary, use the linked Master's ledger/COA identity and then enforce the Master subset | Source-segment resolution after effective ledger/COA completion | No; never default, guess, preserve a literal `SEGMENTn`, or reuse another ledger's column mapping | resolve_source_segment_column_name |
| TreeStructureCode | GL_ACCT_FLEX | A user explicitly assigns a tree and does not supply a TreeStructureCode | No; retain a supplied value unchanged | defer_target_reference_validation_to_import |
| TreeCode | Exact technical `treeCode` resolved from the matching current-target COA row; this is resolution, not a default | A user selects a tree for a segment | No; do not substitute a different COA tree or serialize an unresolved display name | resolve_segment_tree_code |
| TreeStructureCode, TreeCode, DefaultTreeRollupValue | Semantic NULL, serialized as CSV empty strings (`""`) | No hierarchy is selected | No | defer_target_reference_validation_to_import |
| Supplemental Rule `Name` (Business Unit) | Copy the supplied Business Unit name unchanged; otherwise serialize an empty CSV field (`""`) | Every supplied Supplemental Rule; Business Unit is optional | No; never copy `RuleName`, Description, or a prior rule's `Name` into this field. Repeat the same value in linked condition and Detail parent columns. | resolve_supplemental_rule_package_contract |
| Supplemental Rule `Description` | Copy a supplied description unchanged; otherwise serialize an empty CSV field (`""`) | Every supplied Supplemental Rule; description is optional | No; never copy `RuleName`, Business Unit, or a prior rule's Description into this field. | resolve_supplemental_rule_package_contract |
| Supplemental Rule `ControlLevelCode` | No default; exact LookupCode from `resolve_control_level_code` for the rule's own supplied control level | Every supplied Supplemental Rule | No; never inherit the control-budget header control level implicitly | resolve_control_level_code |
| Supplemental Rule `EnabledFlag` | `Y` | A rule is requested and the user does not specify enabled status | No; an explicit disabled choice must serialize as `N`, and an explicit enabled choice as `Y` | resolve_supplemental_rule_package_contract |
| Inherited control-budget segment filter `FilterConditionType` and `FilterConditionCode` | `BUDGET_GL_COA_SEGMENT` and `SEGMENT_VALUE<i>`, with one-based `i` from the parent budget's segment `DisplaySequenceNumber` order | Every parent budget segment for every supplied rule | No; preserve the parent segment order and do not use a COA segment ordinal | resolve_supplemental_rule_package_contract |
| Inherited control-budget segment filter `ApplicableToAllValuesFlag` | `Y`, with no Detail rows | The user supplies no values for that parent budget segment or explicitly chooses All values | No; explicit Specific values requires `N` plus evidenced Detail rows | resolve_supplemental_rule_package_contract |
| Additional Segment Filter `ApplicableToAllValuesFlag` | `Y` with no Detail rows when the user supplies no values; `N` with one linked Detail row per supplied specific value | Every selected additional ledger COA segment, independently of whether a tree is selected | No; preserve explicit specific values and never infer a Detail value from the tree | resolve_supplemental_rule_package_contract |
| Transaction Attribute Filter `ApplicableToAllValuesFlag` | `Y` with no Detail rows for every discovered type whose values are omitted or explicitly All, including `NATURAL_ACCOUNT_TYPE` | Every supplied Supplemental Rule, including when no transaction attributes are mentioned | No; an explicit Specific selection requires `N` and validated technical Detail values. For `NATURAL_ACCOUNT_TYPE`, resolve each Specific value through the filtered BOSS `lookupLists` response and write its returned `lookupCode`; block unmatched or ambiguous values. An explicit `No value` is not All. | resolve_supplemental_rule_package_contract |
| Other condition `ApplicableToAllValuesFlag` | No default; follow the exact declared condition selection and applicable evidence | A supplied condition outside budget segments, additional segments, and transaction attributes | No; do not broaden another condition type to all values | resolve_supplemental_rule_package_contract |
| Supplemental Rule condition tree fields and Detail rows | Empty condition tree fields when no tree is selected; no Detail rows only when `ApplicableToAllValuesFlag` is `Y` | A supplied condition after its exact current-template representation is verified | No; inherited segment filters with Specific values require nonblank user-supplied Detail values, other condition values follow their declared mapping, and a selected tree requires its own evidence | resolve_supplemental_rule_package_contract |


## Default Evidence

| Source ID | Rule Coverage | Evidence Requirement |
|---|---|---|
| P1 | Every default in Standard Defaults | User-supplied prompt table; confirm each field exists in the current same-task template/spec export or approved cross-instance reference baseline. |
| P3 | Forced blank STAT UserConversionType | User-approved clarification, 2026-09-15: Default Rate Type is not permitted for STAT. Always set its value to the actual empty string, including when a rate was supplied or inherited; retain mandatory UOM. P6 supersedes the earlier non-STAT blank default. |
| P4 | CurrencyCode is resolved, not guessed | User-approved currency-name resolution, 2026-09-15; apply STAT-dependent defaults only after final currency resolution. |
| P5 | Summary UnitOfMeasure inheritance | User-approved Summary UOM inheritance, 2026-09-15; reuse the Master's resolved code exactly, without a Summary UOM name lookup. |
| P6 | Required non-STAT UserConversionType, no blank default | User-approved correction, 2026-09-15: enforce the input-validation contract after final currency resolution and Summary inheritance; do not invent a rate or weaken the requirement through a reference baseline. |
| P7 | COA-driven source-segment column resolution | User-approved clarification, 2026-09-16: resolve each Detail/Master source segment's column from the exact ledger's BOSS COA metadata. The user-facing control-budget segment name is distinct from the COA source segment name; Summary reuses its Master's resolved column. |
| P8 | Funds Release Timeframe contract | User-confirmed clarification, 2026-09-17: Master/Detail always serializes `RELEASE_IMMEDIATELY`; Summary defaults to it only when omitted, otherwise resolves the supplied display value through `ORA_XCC_CB_FUNDS_REL_TIMEFRAME` and serializes the returned LookupCode. |
| P9 | Conditional tree-code resolution | User-approved clarification, 2026-10-01: resolve only a selected tree using its exact source segment's current-target COA result; leave tree fields empty when no tree is selected. |
| O1 | Overrides, trees, revenue funding | Oracle Financials 26c Control Budgets page; apply only when compatible with the documented option. |
| E1 | Header and segment semantics | Supplied XCC EDM pages; do not treat an EDM label as import-code evidence. |
| X1 | Supplemental Rule CSV representation | Current same-task template and applicable data export establish rule/condition/detail links and conditional empty fields; verify target applicability before applying any rule-level default. |
| P10 | User-supplied Control Budget Segment Filter mapping, 2026-10-05 | Each requested rule covers every parent budget segment in header order; `BUDGET_GL_COA_SEGMENT` / `SEGMENT_VALUE<i>` follows one-based position and omitted segment values mean All. |
| P11 | User-confirmed Supplemental Rule enabled default, 2026-10-05 | The UI enables a newly created rule by default; omit an enabled choice from user input only, not from the CSV. Write `Y` unless the user explicitly disables the rule. |
| P12 | User-confirmed segment-value validation boundary, 2026-10-05 | Copy nonblank user-supplied specific values for inherited budget segment filters to Detail rows after local checks; Fusion import validates target membership. |
| P13 | User-confirmed Additional Segment Filter defaults, 2026-10-06 | An additional filter may name only its ledger COA segment. An omitted value selection means All values with no Detail rows, whether or not the user also selects a tree. A supplied tree version is copied unchanged for Fusion import validation. |
| P14 | User-confirmed Supplemental Rule Business Unit mapping, 2026-10-07 | Business Unit is optional at the Supplemental Rule header. Copy its supplied name unchanged to `Name`, or write `""` when omitted; keep Description and `RuleName` independent and repeat `Name` in condition and Detail parent links. |

## Revenue Funding Rule Defaults

| Field | Default Value | Applies When | Can User Override? | Resolver |
|---|---|---|---|---|
| RuleName | No default; required | Revenue rule supplied | Yes, supply name | resolve_revenue_rule_package_contract |
| Description | True empty string | Omitted description | Yes, preserve supplied text | resolve_revenue_rule_package_contract |
| EnabledFlag | Y for a requested new rule | Enabled choice omitted | Preserve explicit Y or N | resolve_revenue_rule_package_contract |
| Maximum and minimum limit types | No default; require both explicit choices | Every Revenue rule | Supply applicable choices | resolve_revenue_limit_type_code |
| Fixed amount fields | No default; strictly positive required only for Fixed amount | Applicable limit | Supply amount | resolve_revenue_rule_package_contract |
| Scenario fields | No default; nonblank required only for Revenue estimate | Applicable limit | Preserve supplied scenario name | resolve_revenue_rule_package_contract |
| Primary Balancing and Natural Account selection | Specific; no default values | Columns proved by GL_BALANCING and GL_ACCOUNT labels | User supplies at least one value; All is rejected | resolve_revenue_source_segment_roles |
| Other source segment selection | All, ApplicableToAllValuesFlag Y, no Detail rows | Omitted other-segment selection | Specific requires at least one supplied value and flag N | resolve_revenue_rule_package_contract |
| Source sequenceNumber | No default; retain the current selected-source BOSS COA detail value | Every source COA segment | No user override or guessed sequence; satisfy the Revenue-source COA metadata input check | resolve_revenue_source_coa |
| Target-account condition | TARGET_FUNDING_BUDGET_ACCOUNT and flag N | Every Revenue rule | Accounts and percentages are user inputs | resolve_revenue_rule_package_contract |
| RevFundingPercentage | True empty string on source Detail rows | Revenue-source Specific values | Populate only target-account Detail percentages | resolve_revenue_rule_package_contract |

Do not inherit Supplemental Rule condition types, trees, SEGMENT_VALUE indexes, business units, tolerances, or descriptions into Revenue rows. Inapplicable fixed-amount/scenario columns are empty. Do not change parent AllowRevenueFundingFlag or existing defaults when Revenue rules are absent.

## Override Rule Defaults

These defaults apply only to requested new Override Rules after the Control Budget gate. They do not change existing Supplemental/Revenue defaults, auto-enable AllowOverridesFlag, or generate a rule when none was requested. Omitted parent MaximumOverrideAmount retains the existing semantic NULL/empty CSV default except where an enabled Insufficient Funds rule requires a positive covering maximum under ora_input_validation.md.

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| OverrideName | No default; use the required ruleName | Every requested Override rule | No; preserve supplied name after local validation | resolve_override_rule_package_contract |
| Description | True empty string | Description omitted | No; preserve supplied text | resolve_override_rule_package_contract |
| EnabledFlag | Y | Enabled choice omitted for a requested new rule | Preserve explicit Y or N; this is an FSCR new-rule default, not an asserted Oracle default | resolve_override_rule_package_contract |
| OverrideTypeCode | No default | Every requested rule | Require the declared exact lookup result | resolve_override_type_code |
| OverrideAmount | No default for Insufficient Funds; true empty string for Closed Period only when no amount was supplied | Selected type is resolved | Do not discard a conflicting Closed Period amount; report it | resolve_override_rule_package_contract |
| AllTransactionTypesFlag | Y for transactionTypes.selection All or all five unique supported codes; N for a proper Specific subset | Every requested rule | No; Specific requires nonempty resolved values and all five normalize to All | resolve_override_transaction_type_codes |
| AllJournalSourcesFlag and AllJournalCategoriesFlag | Derived from the source/category state matrix below | Every requested rule after transaction types resolve | Do not conceal a conflicting explicit selection | resolve_override_rule_package_contract |
| UserName | No default | Every requested rule | Preserve each raw string; require at least one nonblank assignment | resolve_override_rule_package_contract |
| JeCategoryCode for a Specific source with All categories | True empty string in the Journal CSV | One row for each Specific source when category selection is All | No model single-space marker; no user category-marker input | resolve_override_rule_package_contract |

### Override Journal Source and Category State

All means a selection state, not a literal journal source/category value. The five transaction types are the current supported set in ora_reference_lookups.md. A Specific selection explicitly listing all five unique supported codes normalizes to All: AllTransactionTypesFlag Y and no Transaction Type or Journal rows. Retain supplied inputs separately as provenance; do not normalize a malformed or unresolved selection.

| Transaction selection | Journal sources | Journal categories | CSV shape |
|---|---|---|---|
| All, or all five supported types selected | All; not editable | All; not editable | Source/category flags Y; no Journal rows |
| A nonempty subset containing only Requisition, Purchase Order, and/or Invoice | All; not editable | All; not editable | Source/category flags Y; no Journal rows |
| A proper subset containing General Ledger and/or Subledger Accounting, with sources omitted or explicitly All | All initially; editable | All; not editable while sources are All | Source/category flags Y; no Journal rows |
| A proper subset containing General Ledger and/or Subledger Accounting, with exactly one Specific source | Specific; flag N | All initially, or Specific supplied categories; editable | Category flag Y writes the one source with empty JeCategoryCode; category flag N writes the supplied source/category rows |
| A proper subset containing General Ledger and/or Subledger Accounting, with more than one Specific source | Specific; flag N | All; not editable | Category flag Y; one Journal row per supplied source with empty JeCategoryCode |

Specific selections require nonempty locally well-formed string lists. A Specific category is structurally permitted only with exactly one Specific source in the editable case; do not infer a source from a category or broaden a conflicting choice to All. Preserve raw values and their order, including duplicates; source/category identity, excluded values, membership, and duplicate business validation remain for Fusion import. The model's single-space All category convention is not the CSV convention: the same-task CSV evidence establishes an empty field.

Use the explicit source/category All or Specific selectors. Do not query a source/category LOV merely to decide that all available values were selected, infer that one supplied source is the only available source, or rewrite Specific raw rows to All on that basis. Those source-analysis UI edge cases require target identity evidence that this workflow deliberately defers; the documented transaction five-code normalization remains separate.

Source authority: user-supplied Override Rules source analysis, version 2 updated 2026-10-19, supplies the state behavior; explicit user decisions supersede its target-value business checks. The CSV convention is independently evidenced in ora_reference_lookups.md.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| CB.DEFAULT | step | 4 | apply_default | ready->CB.DESIGN;blocked->CB.DESIGN | CB.LOOKUP | continue | Apply Control Budget header, budget-segment, and assigned-tree defaults after their applicable lookups. Collect independent failures for the budget gate; do not apply Supplemental Rule defaults yet. |
| CB.SUPP.DEFAULT | step | 10 | apply_default | ready->CB.SUPP.DESIGN;blocked->CB.SUPP.DESIGN | CB.SUPP.LOOKUP | continue | After the budget gate passes, apply rule header and filter defaults to every supplied rule: omitted enabled choice Y, inherited segment condition codes from parent order, and omitted values in budget, additional, and discovered Transaction Attribute filters as All with no Detail rows. Collect independent failures across rules; never infer a rule control level or another condition type's code. |
| CB.REV.DEFAULT | step | 15 | apply_default | ready->CB.REV.DESIGN;blocked->CB.REV.DESIGN | CB.REV.LOOKUP | continue | Apply only Revenue defaults: empty omitted description, new-rule EnabledFlag Y unless explicit choice, All for nonqualified source segments. Both qualified roles stay Specific without generated values; both limit choices remain required. Never change parent funding flag or Supplemental defaults. |
| CB.OVR.DEFAULT | step | 19 | apply_default | ready->CB.OVR.DESIGN;blocked->CB.OVR.DESIGN | CB.OVR.LOOKUP | continue | Apply only requested Override defaults: new-rule EnabledFlag Y, omitted Description empty, transaction flags and source/category state matrix. Never generate names/types/amounts/users, auto-enable the parent, alter supplied raw strings, or mask explicit selection conflicts. Preserve independent rule-group findings. |
