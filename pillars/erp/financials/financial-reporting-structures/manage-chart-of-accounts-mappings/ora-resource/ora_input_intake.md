# Input Intake

## Accepted Input Formats

| Input Format | What Must Be Provided | Applies To |
|---|---|---|
| Mapping design | Mapping name, source chart, target chart, description, optional SecurityFlag, optional import mode, optional intended accounting date, and requested rule activities | All mappings |
| Segment-rule table | Target segment, mapping method, source segment when required, constant target value when required, and rule intent | Segment rules |
| Rollup-rule table | Target segment and value, one or two source segments, detail values or parent values, hierarchy evidence, and accounting date | Rollup rules |
| Account-rule table | Complete target account combination, source detail values, coherent ranges or permitted parents, description, exception rationale, and current export-derived FSM contract evidence | Account rules |
| Current Oracle XLSM | Unmodified current Chart of Accounts Mapping Rules Import workbook with instructions, tooltips, macros, and original column order | FBDI segment and rollup rules |
| Current target template/spec ZIP | CSV headers and ASM_SETUP_CSV_METADATA.xml, checked against the Reviewed FSM Schema and Reviewed FSM Field Semantics sections in ora-resource/ora_reference_lookups.md | FSM preparation; no full data export required |
| Current target mapping evidence | Exact-name header, rules, provenance, coverage, and audit metadata | Existence and comparison before submission; unrelated exports are contract evidence only |

## Dependency Inputs

| Field | Mandatory | Purpose | Send in Request Body? | Lookup Rule |
|---|---|---|---|---|
| Project ID | Yes | Durable artifact and token-usage location | No | Validate safe project path |
| Environment identity | Yes | Bind evidence and approvals to one Fusion environment | No | Resolve through existing authentication skills |
| Intended accounting date | Conditional | Validate values and effective hierarchy versions | No | Use the user-supplied business date; when absent, default to the current date when the run is prepared and record that derivation |
| Security flag | No | Control mapping security behavior | Template decides | Use user-supplied value; otherwise default to N |
| Import mode | No | Control supported FSM task-CSV change behavior | Template or import contract decides | Use user-supplied mode; otherwise default to Increment |
| Import route | No | Select the supported transport after rule composition | No | Default to FSM task-CSV for a header, segment rules, single-source rollups, or account rules; select FBDI only for multiple-source rules or an explicit FBDI request |
| Mapping name | Yes | User-facing existence key and FBDI parent reference | Template decides | Exact name lookup, maximum 33 characters |
| Source chart of accounts | Yes | Resolve the single source parent | Template decides | Match one enabled chart and obtain supported technical identity |
| Target chart of accounts | Yes | Resolve the single target parent | Template decides | Match one enabled chart and obtain supported technical identity |
| Current FBDI template evidence | Conditional | Establish exact FBDI columns, codes, lengths, CSV files, and ZIP shape | No | Required only when multiple-source rules are requested or the user explicitly selects FBDI |
| Existing mapping evidence | Required for submission; pending is allowed for local preparation | Prevent duplicates and unsafe updates | No | Search by mapping name, then compare parent and child definitions |

## Body Field Rules

| Situation | What Happens |
|---|---|
| No approved secondary-ledger or cross-ledger mapping requirement | Do not initiate mapping discovery, export, FBDI preparation, or application workflow. Record the task as not applicable to the COA baseline. |
| UI label is supplied for a technical import field | Treat it as an unresolved candidate until the current template, same-task export, or supported metadata proves the accepted value. |
| Existing mapping is identical | Return the existing definition and stop before create or import. |
| Existing mapping differs | Produce field-level differences and request update versus distinct-mapping direction. |
| Account rules are requested | Collect them for overlap analysis; exclude them from every FBDI artifact and prepare them only through the current export-derived FSM task-CSV contract. |
| Only header, segment, single-source rollup, or account rules are requested and no FBDI route is explicitly requested | Select FSM task-CSV import; do not request or probe an FBDI workbook. |
| Multiple-source rules are requested | Select the Chart of Accounts Mapping Rules FBDI route; do not invent a multiple-source FSM CSV row. |
| Security flag, import mode, or accounting date is omitted | Default SecurityFlag to N, mode to Increment, and accounting date to the current preparation date; retain any user-supplied value instead. |
| Replace mode is requested | Require a complete replacement proof and explicit approval; otherwise use Increment. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.COLLECT | step | 1 | collect_input | valid->COAMAP.VALIDATE | none | stop | Always |
