# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Collect | Obtain mapping identity, rule design, accounting date, environment, and current FSM task-CSV evidence; obtain FBDI evidence only when that interface is selected |
| 2 | Lookup source COA | Resolve one enabled source COA through chartOfAccountsLOV; block mapping submission when missing, disabled, or ambiguous |
| 3 | Lookup target COA | Resolve one enabled target COA through chartOfAccountsLOV; block mapping submission when missing, disabled, or ambiguous |
| 4 | Compare mapping | Acquire the target template first; compare current target mapping evidence when available. Identical terminates; differences need direction; pending permits local preparation only |
| 5 | Resolve conditional metadata | Resolve segments, value sets, values, hierarchies, and structure metadata; export structure metadata only when supported evidence cannot resolve it |
| 6 | Default | Preserve user-supplied SecurityFlag, import mode, and accounting date; otherwise apply N, Increment, and current preparation date, then record evidence |
| 7 | Validate | Enforce EO, VO, mapping, rule, hierarchy, selected-import-contract, concurrency, and approval rules |
| 8 | Readiness | Produce a pass or fail record before preview |
| 9 | Execute | Route only the explicitly approved supported action |

## Design Rules

| Rule ID | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|
| COAMAP.001 | Always | Error | find_source_coa, find_target_coa | Source or target chart is absent, disabled, ambiguous, or identical without an explicit approved business justification | Correct the chart identity or record the approved same-COA justification | Yes |
| COAMAP.002 | Header create or update | Error | find_mapping_definition | Mapping name is blank or longer than 33 characters | Supply a compliant name | Yes |
| COAMAP.003 | Header create or update | Error | find_mapping_definition | Application description is longer than 240 characters | Shorten the description | Yes |
| COAMAP.004 | Existing header found | Error | find_mapping_definition | Requested and existing parent or child definitions differ without direction | Choose update or a distinct mapping | No |
| COAMAP.005 | Approved update | Error | find_mapping_definition | Audit or version evidence changed after comparison | Refresh, compare, and approve again | No |
| COAMAP.044 | Mapping create | Error | resolve_segment_value_set | Header has no rule definition, or a segment-rule design omits an enabled target segment or uses its wrong value set | Supply validated rules and prove complete target coverage before Data Loader approval | Yes |
| COAMAP.006 | Segment rule | Error | find_target_coa | Target segment does not exist in the target chart | Correct the segment | Yes |
| COAMAP.007 | Source-dependent segment rule | Error | find_source_coa | Referenced source segment does not exist | Correct the segment | Yes |
| COAMAP.008 | Segment rule | Error | resolve_segment_map_method | Mapping method is not one of the three documented methods or technical code is unproved | Use a current-template accepted method | Yes |
| COAMAP.009 | Assign single value | Error | resolve_mapping_values | Target constant is missing, invalid, inactive, or ineffective | Select a valid target value | Yes |
| COAMAP.010 | Copy value | Error | find_source_coa, find_target_coa | Source and target value sets do not contain identical permitted values | Use rollup rules or align the value sets | Yes |
| COAMAP.011 | Rollup rule | Error | resolve_mapping_values | Target or source detail value is invalid for the accounting date | Correct the values | Yes |
| COAMAP.012 | Parent rollup | Error | resolve_mapping_hierarchy, verify_hierarchy_association | Hierarchy, version, association, flattening, audit, active state, or deployment is not ready | Complete hierarchy readiness | Yes |
| COAMAP.013 | Segment rules | Error | find_mapping_definition | More than one rule exists for the same mapping and target segment | Treat as update or conflict | No |
| COAMAP.014 | Two-source rule | Error | find_source_coa, find_target_coa | Source count is not exactly two, method is not Use rollup rules, or operator is not Equal to | Correct the rule | Yes |
| COAMAP.015 | Two-source and single-source rules share a target | Error | find_mapping_definition | Single-source rule does not use Use rollup rules | Change the single-source method | Yes |
| COAMAP.016 | Two-source rule | Error | resolve_mapping_values | Duplicate source-value pair or conflicting target result exists | Remove or reconcile the duplicate | Yes |
| COAMAP.017 | Account rule | Error | find_target_coa | Target combination is incomplete, nonexistent, or invalid | Select a valid complete target combination | Yes |
| COAMAP.018 | Account source criteria | Error | resolve_mapping_values | Selector is unsupported, range is incoherent, or parent use is invalid | Use supported detail, range, or permitted parent criteria | Yes |
| COAMAP.019 | Account parent selector | Error | resolve_mapping_hierarchy | Parent is not for a supported primary balancing or natural account segment or hierarchy is ineffective | Correct the selector | Yes |
| COAMAP.020 | Account rule | Error | find_mapping_definition | Logical target-plus-source identity duplicates or materially overlaps another account rule without decision | Reconcile the account rules | No |
| COAMAP.021 | Account rule | Error | none | Description exceeds 1,000 characters | Shorten the description | Yes |
| COAMAP.022 | Account and segment rules coexist | Error | analyze_rule_overlap | Overlap analysis is incomplete | Complete analysis and disclose precedence | Yes |
| COAMAP.023 | FBDI mapping-rules package | Error | inspect_current_fbdi | Account-rule data is present | Remove account rules from the FBDI package; use the export-derived FSM task-CSV contract instead | Yes |
| COAMAP.040 | Data Loader FSM account-rule package | Error | inspect_current_fsm_task_csv | ORA_GL_AFF_MAP_RULE.csv, its export-derived header, matching task metadata, or parent mapping reference is absent or altered | Re-export the task and regenerate the package from the current contract before Data Loader submission | Yes |
| COAMAP.024 | FBDI package | Error | inspect_current_fbdi | Template is not current, columns changed or deleted, code guessed, or ZIP shape differs | Rebuild from the current template | Yes |
| COAMAP.025 | FBDI package | Error | resolve_mapping_values, resolve_mapping_hierarchy | Any row or parent-child reference is invalid or unresolved | Correct all rows before submission | Yes |
| COAMAP.026 | Replace | Critical | find_mapping_definition | Package is partial or explicit Replace approval is absent | Use Increment or supply a complete approved set | No |
| COAMAP.027 | Any mutation | Critical | find_mapping_definition | Exact environment-bound approval is absent | Obtain explicit approval | No |
| COAMAP.028 | Technical import field | Error | select_import_route | UI label, physical column, table ID, or guessed default is used without accepted-value evidence | Resolve from the current template, export, or supported metadata | Yes |
| COAMAP.029 | Hierarchy-dependent rule | Warning | resolve_mapping_hierarchy | Duplicate children or optional Essbase publication constraints affect another use | Disclose the constraint; do not require Essbase solely for mapping | No |
| COAMAP.030 | Readiness | Error | all applicable resolvers | Any required check remains unresolved for the requested stage; a pending mapping comparison blocks submission but not contract-based local preparation | Resolve every submission blocker before Data Loader preview; label local preparation separately | Yes |
| COAMAP.031 | Mapping header | Error | find_mapping_definition | A duplicate mapping name is detected | Resolve GL_DUP_COA_MAPPING_NAME by selecting a distinct name or approved update path | Yes |
| COAMAP.032 | Copy value | Error | resolve_value_set_max_size | Source value-set maximum size exceeds target value-set maximum size | Use another mapping method or a compatible target value set | Yes |
| COAMAP.033 | Segment metadata | Error | resolve_segment_value_set | Segment metadata is not enabled or does not belong to the exact resolved COA | Correct the segment or COA selection | Yes |
| COAMAP.034 | Segment method | Error | resolve_segment_map_method | Method code is not S, C, or R for normal creation, or the selected-route contract is incompatible | Use a supported, evidence-backed method | Yes |
| COAMAP.035 | Rollup rule | Error | resolve_mapping_values | Populated target value lacks source low or high value, Between range is reversed, or rules overlap | Correct bounds and remove or reconcile overlap | Yes |
| COAMAP.036 | Constant, copy, or rollup rule | Error | find_value_set_definition | The segment-derived value set does not resolve to exactly one definition or its metadata is incompatible with the requested rule | Correct the verified value set or rule design | Yes |
| COAMAP.037 | Constant target value | Error | find_value_set_values | Target value is absent, disabled, ineffective, ambiguous, or lacks required dependent-value context | Supply a valid target value for the accounting date | Yes |
| COAMAP.038 | Copy value | Error | find_value_set_values, resolve_value_set_max_size | Complete active source and target value populations are not identical, paging is incomplete, or source maximum length exceeds target | Use rollup rules or align compatible value sets and values | Yes |
| COAMAP.039 | Rollup rule | Error | find_value_set_values | A source bound or target value is absent, disabled, ineffective, ambiguous, or unverified in the resolved child-values collection | Correct the rule values and rerun lookup | Yes |
| COAMAP.041 | Readiness | Error | resolve_execution_defaults | Resolved SecurityFlag, import mode, or accounting date is absent, or a defaulted value is not recorded as such | Resolve and record user precedence or the documented default | Yes |
| COAMAP.042 | Import-route selection | Error | select_import_route | A live import bypasses core.data-loader, or a multiple-source mapping has no Data Loader-authorized FBDI adapter | Select the Data Loader FSM ZIP path for supported mappings; stop when no approved Data Loader adapter supports the requested FBDI package | Yes |
| COAMAP.043 | Any live import | Critical | none | A direct FSM endpoint or another import adapter is selected instead of core.data-loader | Submit the approved package through core.data-loader only. | Yes |

## Design Lookup Requirements

| Rule ID | Resolver | When Required | Values Needed | Source File |
|---|---|---|---|---|
| COAMAP.001 | find_source_coa, find_target_coa | Always | Chart identity, enabled state, segments, value sets | ora_reference_lookups.md |
| COAMAP.004 | find_mapping_definition | Before create or update | Header, rules, audit metadata | ora_reference_lookups.md |
| COAMAP.010 | find_source_coa, find_target_coa | Copy-value rule | Complete permitted value sets | ora_reference_lookups.md |
| COAMAP.012 | resolve_mapping_hierarchy, verify_hierarchy_association | Parent-based rule | Tree, version, dates, state, association, deployment | ora_reference_lookups.md |
| COAMAP.022 | analyze_rule_overlap | Mixed rule types | Normalized source criteria and target results | ora_reference_lookups.md |
| COAMAP.024 | inspect_current_fbdi | FBDI generation | Current workbook contract and fingerprint | ora_reference_lookups.md |
| COAMAP.040 | inspect_current_fsm_task_csv | FSM account-rule import | ORA_GL_AFF_MAP_RULE.csv header, metadata, parent mapping reference, and ZIP shape | ora_dependency_readiness.md |

## Validation Messages

| Message ID | Message |
|---|---|
| COAMAP-E001 | Mapping blocked: source or target chart of accounts did not resolve uniquely to an enabled chart. |
| COAMAP-E004 | Mapping already exists with differences. Review the field-level comparison and choose update or a distinct name. |
| COAMAP-E013 | Duplicate target-segment rule detected. A mapping can contain only one segment rule per target segment. |
| COAMAP-E014 | Multiple-source mapping requires exactly two source segments, Use rollup rules, and Equal to. |
| COAMAP-E022 | Account-rule precedence cannot be confirmed because overlap analysis is incomplete. |
| COAMAP-E023 | Account rules are not supported by Chart of Accounts Mapping Rules Import. Use the export-derived FSM task-CSV route, not the FBDI workbook. |
| COAMAP-E040 | FSM account-rule import is blocked: the current export-derived ORA_GL_AFF_MAP_RULE.csv contract or matching metadata is missing or altered. |
| COAMAP-E026 | Replace rejected: the package is partial or complete-replacement approval is missing. |
| COAMAP-E028 | Technical value unresolved: replace the UI label or guessed value with template, export, or supported metadata evidence. |
| COAMAP-E030 | Live import blocked: first-go import readiness failed. |
| COAMAP-E031 | Duplicate mapping name detected: GL_DUP_COA_MAPPING_NAME. Select a distinct name or an approved update path. |
| COAMAP-E032 | Copy value rejected: source value-set maximum size exceeds target value-set maximum size. |
| COAMAP-E033 | Segment metadata could not be confirmed for the resolved chart of accounts. |
| COAMAP-E034 | Mapping method is not supported by EO/VO and current-template evidence. |
| COAMAP-E035 | Rollup rule is incomplete, reversed, duplicate, or overlapping. |
| COAMAP-E036 | Value-set definition could not be resolved uniquely from the verified segment metadata. |
| COAMAP-E037 | Target constant is not an enabled, effective value for the resolved value set. |
| COAMAP-E038 | Copy value rejected: active source and target value populations are not proven identical. |
| COAMAP-E039 | Rollup rule references a source or target value that is not valid for the accounting date. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.ENFORCE | step | 9 | design_enforcement | valid->COAMAP.BULK | COAMAP.DEFAULT | stop | New mapping, approved update, or local preparation with pending comparison |
