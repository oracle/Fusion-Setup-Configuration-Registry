# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Create identity | Status Name; optional Internal Name; operation=create | Stop with missing Status Name | Use the supplied Internal Name, or derive it after the fresh populated export by replacing whitespace runs in Status Name with `_`; map the resolved value to StatusInternalName | Create | resolve_new_change_status_identity |
| Supported operations | Create or Update | Stop | Reject Delete; this skill does not support deleting a change status. | Every request |  |
| Update identity and changes | One of: Existing Internal Name; Existing Status; Existing Status with Existing Status Type; Existing Internal Name with Existing Status; Existing Internal Name with Existing Status Type; or Existing Internal Name with Existing Status and Existing Status Type. Also require operation=update and one or more of New Status, Description, or Status Type changes. | Stop with missing fields | Always use the supplied selector values to find current rows in a fresh populated target export, including for Existing Internal Name. Copy the full selected export row into the ZIP and change only requested fields. Existing Status alone selects every matching row; proceed when exactly one row matches, otherwise require explicit bulk-scope approval before artifact preparation. Existing Status Type alone is not accepted. | Update | resolve_existing_change_status |
| Business purpose and status category | Optional Operational Purpose; StatusTypeName | Do not require Operational Purpose; do not infer a category from the name | When Operational Purpose is supplied, map it to Description. When StatusTypeName is absent, show the fixed catalog and ask the user to select one | Create | resolve_change_status_type |
| FSM schema evidence | Target-environment template ZIP with ASM_SETUP_CSV_METADATA.xml and EGO_CHANGE_STATUS.csv | Stop | Use shared.setup-export.task-level-export in template mode | Preparing an import |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Create identity and purpose | Reject blank Status Name. Operational Purpose is optional; when supplied, map it to Description. A supplied Internal Name must not contain whitespace; when omitted, derive and validate it only after reviewing the fresh populated export. | Create | resolve_new_change_status_identity |
| Update target and changed fields | Reject an update with neither Existing Status nor Existing Internal Name, or with no supported changed field | Update | resolve_existing_change_status |
| Status category | Require a StatusTypeName from the fixed catalog and map it case-insensitively to the numeric import value | Create or Status Type update | resolve_change_status_type |
| Update selector checks | When supplied as selectors, require Existing Status and Existing Status Type to match the exported row. Existing Status alone applies the requested change directly when one row matches; when multiple rows match, obtain explicit bulk-scope approval first. New Status and Status Type are separate requested update values. | Update | resolve_existing_change_status |
| SeededFlag | Internal-only field; do not ask for, display, or validate it as user input. Apply its create-only default from ora_defaulting_rules.md. For Update, require the value to remain exactly as exported under the update import-row preservation check. | Preparing an import |  |
| FSM field mapping | Map Status Name to StatusName, Internal Name to StatusInternalName, and supplied Operational Purpose to Description. | Preparing an import |  |
| New-status identity | Before ZIP preparation, use a fresh populated target EGO_CHANGE_STATUS.csv to reject an existing StatusName or StatusInternalName. If Internal Name was omitted, derive the candidate by replacing whitespace runs in Status Name with `_`; reject it if it still contains whitespace or conflicts with an exported row. | Create | resolve_new_change_status_identity |
| End Date | When supplied, show: Warning: Change Status End Date is not supported by the import/export process and will be skipped. Do not map, default, derive, or invent an End Date column. Continue with other supported requested changes; if no supported change remains, do not prepare an import artifact. | Update | |
| Update-only fields | For Update, use the supplied or resolved `StatusInternalName` only to select the exported row. Copy the complete selected row, including StatusName, StatusType, ObjectName, SeededFlag, and every other exported carrier, then apply only requested StatusName, Description, or StatusType values. Never construct an update row from a template or user input alone. Map a Status Type through the fixed catalog. | Update | resolve_existing_change_status |
| Update import-row preservation | Before presenting import approval, compare every prepared update row with its selected fresh-export row. Require every non-requested column to be present and unchanged; regenerate from the export if it differs or is blank. Do not preview, ask the user to choose a safer flow, or submit a partial row. | Update | resolve_existing_change_status |
| Non-updatable fields | Reject an update request that changes Internal Name or Active and stop. Existing Internal Name is allowed only as the update selector. | Update |  |
| Data authority | Use the user-authorized current setup export and template from the exact target environment; reject another environment or an older artifact superseded in this run | Preparing an import |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MCS.INPUT | step | 10 | validate_input | valid->MCS.LOOKUPS;invalid->RETURN_ISSUES | none | stop | A Manage Change Statuses request is supplied |
