# Defaulting Rules

## Source Precedence

| Sequence | Source | Use |
|---|---|---|
| 1 | Current target FSM template/spec ZIP, ASM_SETUP_CSV_METADATA.xml, and the Reviewed FSM Schema and Reviewed FSM Field Semantics sections in ora-resource/ora_reference_lookups.md | Exact CSV structure plus verified field and S/C/R method semantics; no populated full-task export required |
| 2 | Current Oracle FBDI XLSM and generated metadata | Exact FBDI worksheets, columns, required values, import codes, field limits, CSV files, and ZIP shape |
| 3 | Supported read-only Fusion metadata | Environment-specific identifiers, existing definitions, technical values, hierarchy versions, and accepted value forms |
| 4 | Oracle functional documentation | Supported methods, precedence, sequencing, and import behavior |
| 5 | Oracle Enterprise Data Model documentation | Object meaning, relationships, application lengths, identity, and concurrency evidence |
| 6 | User-approved business design | Mapping intent, descriptions, exceptions, accounting date, and update decisions |

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? |
|---|---|---|---|
| Security flag | N | User does not supply SecurityFlag | Yes; user-supplied SecurityFlag takes precedence |
| Import mode | Increment | User does not supply import mode for any supported FSM task-CSV mapping change, including account rules | Yes; user-supplied mode takes precedence, and Replace still requires explicit approval and complete-replacement proof |
| Accounting date | Current date when the run is prepared | User does not supply an accounting date | Yes; user-supplied accounting date takes precedence. Record the resolved date and use it consistently for all effective-date checks. |
| Multiple-source mapping method | Use rollup rules | Exactly two source segments map to one target segment | No |
| Multiple-source operator | Equal to | Exactly two source segments map to one target segment | No |
| Account-rule execution route | Export-derived FSM task-CSV package using ORA_GL_AFF_MAP_RULE.csv, submitted through core.data-loader | Account rules are requested | No |
| Standard mapping execution route | FSM task-CSV package submitted through core.data-loader | The design contains only a header, segment rules, single-source rollup rules, or account rules | No; a direct FSM import endpoint is not permitted |
| Multiple-source execution route | Data Loader-authorized FBDI adapter | Exactly two source segments map to one target segment | No; stop when no approved Data Loader adapter supports the FBDI package |
| Source COA, target COA, mapping name, and account-rule decisions | No default | Always | No |
| Segment mapping method | No default except the two-source restriction | Always | No; use S=Assign single value, C=Copy value from source, R=Use rollup rules only for a compatible FSM contract; resolve FBDI codes independently. U is not a normal create method |
| FBDI technical codes and required values | Value proved by the current template, same-task export, or supported metadata | A technical field is required | No |
| Value-set REST item key and child-values URI | Returned by the exact valueSets match | A value-set values lookup is required | No; follow the returned item link and never synthesize the path from ValueSetCode or ValueSetId |
| Object-version metadata | Read-only concurrency evidence | Existing mapping or rule is compared | No; never populate import artifacts unless the current template explicitly requires it |
| Replace omissions | Delete omitted existing segment rules | Replace is explicitly approved | No; disclose before approval |

## Derivation Record

For every generated, defaulted, or derived value, record the output field, resolved value, whether it was user-supplied or defaulted, source type, source location or template fingerprint, lookup time, environment, and whether user approval was required. Do not derive technical codes from physical database columns or UI labels.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.DEFAULT | step | 8 | apply_default | complete->COAMAP.ENFORCE | COAMAP.DEPENDENCIES | stop | New mapping, approved update, or local preparation with pending comparison |
