# Bulk Intake

## Accepted Bulk Inputs

| Input Format | What Must Be Provided | How Rows Are Processed |
|---|---|---|
| Current Oracle Chart of Accounts Mapping Rules XLSM | Original workbook, instructions, tooltips, macros, worksheet and column order | Validate the workbook first, then use its macro to generate the supported CSV and ZIP outputs |
| Segment-rule rows | One parent mapping reference and one unique target-segment rule per mapping and target segment | Normalize, resolve codes, compare existing rules, and validate as one mapping package |
| Single-source rollup rows | Valid parent segment rule, target value, source segment, detail value or effective parent hierarchy | Validate child rows only after the parent segment rule passes |
| Multiple-source rollup rows | Valid parent segment rule, exactly two source segments, target value, Equal to condition, and source value pair | Preserve separately from single-source rollups and reject duplicate pairs |
| Account-rule rows | Complete target combination, source criteria, overlap analysis, and an export-derived FSM account-rule CSV contract | Exclude from the Chart of Accounts Mapping Rules FBDI workbook; process through the supported FSM task-CSV import contract using ORA_GL_AFF_MAP_RULE.csv |

## Import Route Selection

| Rule Composition | Required Route | What Happens |
|---|---|---|
| Header, segment rules, and single-source rollup rules only | FSM task-CSV | Use a current target-environment template/spec ZIP plus the reviewed FSM semantic contract; no populated full-task export or FBDI workbook is required. |
| Account rules, with or without standard rules | FSM task-CSV | Require ORA_GL_AFF_MAP_RULE.csv and matching ASM_SETUP_CSV_METADATA.xml. |
| Multiple-source segment or rollup rules | FBDI | Use the current XLSM and its generated package; do not hand-author an FSM multiple-source row. |
| Explicit user choice of FBDI for supported standard rules | FBDI | Use the current XLSM and disclose that FSM was also available. |

## Column Guidance

| Column Type | Allowed Fields | What Happens |
|---|---|---|
| Template-controlled | Every column in the current Oracle XLSM | Preserve order and never delete; hide or leave unused columns blank only when the template allows |
| Mapping header | Current-template fields for mapping name, source chart, target chart, description, and action | Resolve from business input and supported technical evidence |
| Segment rule | Current-template target segment, method, constant, and source-segment fields | For a compatible FSM contract use S for Assign single value, C for Copy value from source, and R for Use rollup rules; for FBDI resolve codes from its current XLSM |
| Rollup rule | Current-template target and source segment/value, condition, tree, and version fields | Validate values, ranges, parents, and effective dates before CSV generation |
| FSM account rule | Columns and row shape from the current same-task export for ORA_GL_AFF_MAP_RULE.csv | Preserve the export-derived header and only populate fields proven writable by the exported task contract |
| Internal or audit | Status, request, error, audit, physical ID, and version fields not explicitly writable in the current template | Do not populate or manipulate |

## Preview and Execution Rules

| Gate | Requirement |
|---|---|
| Workbook validation | Only for FBDI, run the current XLSM Validate action before its CSV generation. FSM uses template headers, metadata, and local package validation. |
| Template export gate | Obtain the task template/spec ZIP whenever needed through shared.setup-export.task-level-export without --data. No mapping inputs, COA resolution, or existing-mapping comparison are required for template export. |
| Mapping evidence gate | For live create or update, compare current target-environment evidence covering the exact name. Prefer a supported focused read or a scoped export with confirmed criteria. Do not automatically request an unfiltered full-task data export; when no supported focused source is available, comparison remains pending and only local preparation may continue. |
| Structure-export fallback | Export structure metadata only when chartOfAccountsLOV, mapping evidence, supported segment or value-set lookup, and current same-task mapping export cannot resolve required segment or value-set details |
| CSV generation | FSM: preserve template filenames, headers, and metadata; populate only requested mapping rows using the reviewed semantic contract. FBDI: use the XLSM-generated CSV files and ZIP structure. |
| Required files | Confirm the exported task CSV files needed by the requested rules, including ORA_GL_AFF_MAP_RULE.csv when account rules are requested |
| Parent-and-children validation | Validate the header, every segment rule, every rollup, all referenced objects, and all hierarchy dependencies as one structure |
| All-or-nothing | Reject the package locally when any row for a mapping is invalid or unresolved |
| Increment | Use for changes unless Replace is explicitly approved |
| Replace | Prove the package is a complete replacement set and warn that omitted existing segment rules can be deleted |
| Account rules | Never place account rules in the FBDI workbook, CSV files, or ZIP. Include them only in an export-derived FSM task-CSV package using ORA_GL_AFF_MAP_RULE.csv and the matching task metadata. |

## First-Go Import Readiness

| Required Evidence | Pass Condition |
|---|---|
| Mapping identity | Mapping name and source and target charts resolve uniquely |
| Effective date | Intended accounting date is recorded and used for all value and hierarchy checks |
| Template contract | FSM: current target template fingerprint, compatible headers/types/hierarchy, and reviewed field/code semantics. FBDI: current XLSM, worksheets, codes, generated files, and ZIP shape. |
| Derived values | Every generated or defaulted value has a supported evidence source |
| Existing comparison | For submission, current target evidence classifies the header and every rule as new, identical, approved update, conflict, or excluded. Pending evidence permits local preparation only. |
| Overlap analysis | Every account-rule and segment-rule overlap shows the account-rule effective result |
| Approval | Live action and Replace approval, when applicable, are explicit and environment-bound |
| Decision | Pass only when no business decision or technical lookup gap remains |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.BULK | step | 10 | process_bulk | ready->COAMAP.PREVIEW | COAMAP.ENFORCE | stop | New mapping, approved update, or local preparation with pending comparison |
