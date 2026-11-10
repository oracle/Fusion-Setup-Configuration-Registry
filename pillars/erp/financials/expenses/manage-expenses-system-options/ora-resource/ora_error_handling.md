# Manage Expenses System Options Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| The workbook, baseline export, metadata identity, or CSV digest changes after validation | Classify as catalog mismatch; stop and obtain a new export and validation result |
| A requested value is inherited, a dynamic reference, candidate mapping, unmapped field, or an option without an exact confirmed value code | Classify as unsupported_by_confirmed_fsm_contract; identify the field and do not generate a package. Confirmed creates and missing overrides are supported through sparse insertion |
| An option CSV has no exact row, duplicate rows, a mismatched header, or paired option files differ on a requested row | Classify as catalog mismatch; do not choose a row or repair the export |
| The package changes after it is built | Classify as artifact persistence; restart Data Loader preflight, Task Hook validation, and approval with the changed package |
| Data Loader preflight, Task Hook validation, approval, submission, monitoring, or ProcessLog verification fails | Preserve the returned safe diagnostic, stop before retry, and follow core.data-loader's declared recovery path |
| Selected-row nonproduction qualification is locally valid but has no import/read-back evidence | Retain a warning in Task Hook and exact-artifact preview; conformance permits only the declared test, never ordinary customer promotion. Failed unrelated-row or audit preservation remains a failed live test |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMSO.DATA_LOADER_HANDOFF | step | 3 | execution_gate | ready->EXMSO.READY_FOR_DATA_LOADER;blocked->EXMSO.RETURN_ISSUES | EXMSO.CONFIRM_BASELINE | stop | The confirmed package is unchanged and has not been submitted |
| EXMSO.READY_FOR_DATA_LOADER | terminal | 4 | terminal | none | EXMSO.DATA_LOADER_HANDOFF | stop | A confirmed package is ready for mandatory core.data-loader preflight; no import has occurred |
| EXMSO.RETURN_ISSUES | terminal | 5 | terminal | none | none | stop | A validation, baseline, package, or Data Loader handoff blocker prevents completion |
