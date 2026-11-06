# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve |
|---|---|---|---|
| Mapping header | Mapping name, source chart, target chart, description when used, security intent or defaulted SecurityFlag | Block | Collect business input; default SecurityFlag to N only when it is omitted |
| Effective-date context | User-supplied intended accounting date or the defaulted current preparation date | Block | Default the date only when omitted, record the derivation, and use it consistently throughout validation |
| Segment rule | Target segment, method, and method-specific source or target value | Block | Validate against the current template and supported metadata |
| Rollup rule | Target segment and value, source segment details, condition, value or parent selection, hierarchy version when parent-based | Block | Resolve references before workbook generation |
| Account rule | Complete target combination, complete source criteria, optional description, exception rationale, and export-derived FSM account-rule contract | Block | Validate against ORA_GL_AFF_MAP_RULE.csv and ASM_SETUP_CSV_METADATA.xml from the compatible current target template/spec ZIP |
| FBDI contract | Current Oracle XLSM, worksheet tooltips, required columns, CSV names, ZIP structure | Block FBDI | Download the current template; do not invent fields |
| Import-route selection | Rule composition and any user-selected route | Block | Use FSM for header, segment, single-source rollup, and account rules; require FBDI only for multiple-source rules or an explicit FBDI request |

## Dependency-Aware Validation

| Applies When | Result | Next Action |
|---|---|---|
| Referenced chart, segment, value, hierarchy, or hierarchy version is absent, inactive, ambiguous, or ineffective | Blocked | Correct the dependency and rerun readiness |
| Existing mapping evidence is pending | Prepared only | Continue local contract-based preparation; block submission approval until comparison passes or an explicit Task Hook waiver is recorded |
| Existing mapping matches the complete request | Existing identical | Report it and do not create |
| Existing mapping differs | Direction required | Show parent and child differences and obtain explicit direction |
| Mapping changed after initial comparison | Concurrent update | Refresh evidence, invalidate approval, and compare again |
| Account rule overlaps a segment-rule result | Valid with precedence disclosure | Show the overlap and state that the account rule supersedes |

## Field Validation

| Check | What Happens |
|---|---|
| Mapping name | Reject blank names and names longer than 33 characters. |
| Mapping description | Reject values longer than 240 characters at the application level; apply any stricter current-template limit to FBDI fields. |
| Parent relationship | Require exactly one source chart and one target chart for every mapping. |
| Create rule completeness | Reject a header-only create. For segment-rule mappings, require one rule for every enabled target segment; compare the complete current target metadata list and verify each target value-set association. Templates alone do not prove segment or value validity. |
| Target-segment uniqueness | Reject a second segment rule for the same mapping and target segment; treat it as update or conflict. |
| Mapping method | Allow only Assign single value, Copy value from source, or Use rollup rules, using the selected-route contract: reviewed S/C/R semantics plus compatible target template for FSM, current XLSM for FBDI. |
| EO technical method values | Accept S, C, R, or U only when current template or export evidence confirms the code. Treat U as internal delete or update behavior; reject it for normal create unless the current template proves it. |
| Assign single value | Require a valid target value effective on the intended accounting date. |
| Assign single value shape | Require source segment and source value set to be null; require target single value to be populated and valid. |
| Copy or rollup shape | For C or R, require source segment and source value set; require target single value to be null. |
| Copy value | Require source and target value sets to contain identical permitted values; a similar label or format is insufficient. |
| Copy value maximum size | Use resolve_value_set_max_size to verify that source maximum length is less than or equal to target maximum length. Accept MaximumLength from the exact source and target valueSets lookups; CoaValueSetMaxSizeVO evidence is optional corroboration, not an additional prerequisite. |
| Value-set definition | Require exactly one valueSets match for the segment-derived ValueSetCode and validate supported datatype, validation type, subtype, maximum length, and format flags before using the values collection. |
| Constant target value | Require one exact enabled and accounting-date-effective target child value; include independent-value context for a dependent value set. |
| Copy value population | Compare complete paged active source and target child-value populations, including independent-value context for dependent sets. Require identical permitted values, compatible datatype and formatting, and source maximum length less than or equal to target maximum length. |
| Rollup values | Require each target value and every referenced source detail value or range boundary to be exact, enabled, and accounting-date-effective in its resolved child-values collection. |
| Single-source rollup | Require a valid target value and valid source detail values or an effective parent hierarchy. |
| Two-source rollup | Require exactly two valid source segments, one target segment, Use rollup rules, and Equal to. |
| Mixed single and two-source mapping | If the target segment also has a single-source rule, require that rule to use Use rollup rules. |
| Duplicate source pair | Reject duplicate two-source value-pair definitions and conflicting target results. |
| Account target | Require a complete, existing, valid target account combination in the target chart. |
| Account source selectors | Allow detail values, detail-value ranges, and parent values only where Oracle supports them; parent selectors apply to primary balancing and natural account segments. |
| Account range | Require low and high values in a coherent ordered range and effective for the intended date. |
| Account description | Reject values longer than 1,000 characters. |
| Account-rule identity | Compare the target combination plus source filter or range criteria; do not expose the surrogate identifier as the business key. |
| Account-rule import route | Reject every account-rule row from the FBDI mapping-rules package. Permit account-rule rows only in an export-derived FSM task-CSV package containing ORA_GL_AFF_MAP_RULE.csv and matching task metadata. |
| Import route | Reject FBDI selection as a prerequisite for a standard FSM-supported mapping unless the user explicitly requests FBDI. Reject FSM for multiple-source rules until an export-derived multiple-source contract is confirmed. |
| Mapping-name uniqueness | Reject duplicate mapping names and classify GL_DUP_COA_MAPPING_NAME as a duplicate-name error; do not create another mapping. |
| Rollup source bounds | When target value is populated, require both source low and source high values. For Between, require source low less than or equal to source high. |
| Rollup overlap | Reject duplicate or overlapping rollup definitions. |
| Technical value evidence | FSM uses the Reviewed FSM Schema and Reviewed FSM Field Semantics sections in ora-resource/ora_reference_lookups.md only after target-template compatibility passes. FBDI uses its current template. Reject unproved labels, physical IDs, and guessed values. |

## Import Readiness Validation

Require mapping name, charts, resolved accounting date, resolved SecurityFlag, resolved import mode, mapping methods, required files and columns, resolved values, evidence sources, dependencies, existing-object comparison, overlap analysis, approval evidence, unresolved items, and a pass or fail decision. Preserve user-supplied values; otherwise require the documented defaults. Fail when any required technical value, dependency, row, approval, or package-completeness check fails.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.VALIDATE | step | 2 | validate_input | valid->COAMAP.CONTRACT | COAMAP.COLLECT | stop | Always |
| COAMAP.VERIFY | decision | 14 | evaluate_result | verified->COAMAP.DONE_LIVE;pending->COAMAP.DONE_PENDING;failed->COAMAP.ERROR | COAMAP.EXECUTE | stop | Only a later explicit user result request for an accepted load; use the shared Data Loader status workflow |
