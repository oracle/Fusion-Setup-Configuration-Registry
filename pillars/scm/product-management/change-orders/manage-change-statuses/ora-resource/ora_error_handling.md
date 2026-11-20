# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing or unsupported StatusType | Show the fixed numbered StatusType catalog and stop until the user selects by status name or selection number (`1` through `5`) |
| New status has an invalid or duplicate identity after export review | Stop before ZIP preparation. For whitespace in a supplied or derived Internal Name, show: `Internal Name cannot contain spaces. Provide an Internal Name without spaces.` For an existing Internal Name or Status Name, show the matching exported row and direct the user to update it or choose a distinct identity. |
| Delete request | Stop and report that Delete is not supported for Manage Change Statuses. Do not prepare or import an artifact. |
| Update target missing or ambiguous | Stop; do not create a status or select a matching row |
| Existing Status-only selector matches multiple rows | Show all matched Internal Names, Statuses, and Status Types, then stop for explicit approval of the full bulk scope. Do not prepare or import the update before that approval. |
| Update asks to change Internal Name, Active, or Status Code | Stop and report that the field is not supported for update. Existing Internal Name is allowed only as the selector. |
| End Date is requested | Show: Warning: Change Status End Date is not supported by the import/export process and will be skipped. Omit End Date and continue with other supported requested changes; if no supported change remains, do not prepare an import artifact. |
| Update row omits StatusName or StatusType | Stop and rebuild from the current export with StatusName, StatusType, and ObjectName retained unchanged; FSM rejects a partial row without those mandatory carriers. |
| Fusion rejects one or more Change Status rows | After Fusion returns its result, show one Change Status import results table containing every submitted status, using the canonical Backend row failures disclosure below. State only the backend reason supplied by Fusion; do not invent a more specific rule. After the table, say: The import was unsuccessful because of the errors shown above. Please correct the rows with errors and upload all the data again. |
| FSM import failure or uncertain result | Preserve safe process evidence; reconcile before another write |
| Changed artifact after preview | Restart validation and approval for the changed bytes |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Validation | Exact task, passed path, missing fields, evidence, blockers, and safe resume step |
| Approval | Exact environment, status name, internal code, type, purpose, and validated artifact |
| Backend row failures | The canonical Change Status import results table contains every submitted status and uses these columns in order: Status Name, Internal Name, Status Type, Description, Requested Change, Result, Reason / Backend Error, Marker. Show the Status Type name, not its numeric import value. Use ❌ for a Fusion-rejected row and ✅ for a row with no Fusion row error; Marker describes row-error presence, not application success. If the batch rolled back, set Result to Not applied — batch rolled back even for a row marked ✅; otherwise state the evidenced applied outcome. |
| Secrets | Never disclose OAuth tokens, secrets, or protected runtime material |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Failed validation | Do not present approval or upload the archive |
| Missing standalone import approval | Do not upload or initiate; a successful rule plan is not approval |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RETURN_ISSUES | terminal | 90 | terminal | none | none | stop | A reached validation rule returns a missing, invalid, or conflicting outcome |
| MCS.RETURN_SUCCESS | terminal | 100 | terminal | none | MCS.DESIGN | stop | All pre-preview task rules pass; return validation evidence to Data Loader without authorizing import |
