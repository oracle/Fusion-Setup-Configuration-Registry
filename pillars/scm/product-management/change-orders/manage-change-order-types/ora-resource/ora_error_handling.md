# Manage Change Order Types Error Handling and Import Gate

Source: user requirements for validation without confirmation, exact ZIP review before import, unique copied identities, complete dependencies, and child header-row exclusion.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Internal Name contains invalid characters | Classify as input validation; show exactly: error: "You must enter numbers, letters, and underscore (_) characters or any combination of these." Prompt the user to change Internal Name and revalidate; do not sanitize punctuation or prepare the creation package |
| Constructed Internal Name awaits confirmation | Show the exact candidate and ask for confirmation or a replacement. Wait before preparing the creation package; this user-requested confirmation is separate from ZIP/import approval |
| New identity is already used or Category Code mapping is unresolved | Stop before package preparation; ask for a different Internal Name for a collision, or report the missing/ambiguous mapping. Do not copy source identity/category, invent a suffix, or omit Category Code |
| Default Assignee missing, blank, or explicitly cleared | For Create/cloning or Update, first resolve source/existing values plus explicit overrides. Copy a complete unchanged source pair without prompting. Only when the effective role is present and assignee remains blank/missing, stop before export/import and ask: Please provide a Default Assignee user who belongs to the selected Assignee Role '<assignee role>'. Explicit clear is not refilled; an unchanged invalid pair also blocks. With no effective role, allow blank and do not prompt |
| Default Assignee membership is unclear or mismatched | With a present effective role, clarify uncertain membership for a new/changed pair or request a suitable member for a known mismatch before export/import. A complete unchanged source pair may be copied without re-entry or membership reconfirmation; do not claim independent verification. Block any known mismatch, including a baseline mismatch. With no role, skip membership prompting. Do not change memberships |
| Sequence Generated numbering details are missing | Classify as input validation; stop before export/import and ask: Sequence Generated numbering requires Prefix or Suffix, Starting Number, and Increment. Please provide: <missing fields>. List only missing fields, asking for Prefix or Suffix only when both are blank or absent. Wait for the response and revalidate; do not default missing details or treat this as import approval |
| Stale route-step parent, mismatched status sequence, or unresolved workflow lineage | Classify as input validation and block approval/upload. Rebuild from the selected export and request-backed status/route mapping; retain technical row evidence internally. Remove a stale duplicate only after proving its complete remapped row is represented exactly once. If stage inheritance remains ambiguous, ask only for the missing workflow decision; never map by sequence alone, drop required dependencies, or retry import automatically |
| Duplicate or conflicting ORA_EGO_WORKFLOW_STATUS_CONTROL target status/action rows | Block upload/import; retain conflicting keys and row evidence in diagnostics. Consolidate exact duplicates or apply explicit edits to the baseline row; stop on unresolved conflicting values rather than choosing an arbitrary row. Do not automatically retry a failed import |
| Role Code is missing or blank for a requested role assignment | Classify as input validation; stop and show: Role Code is missing from your request. Please provide the Role Code for the role you want to assign. Do not prepare or submit the affected assignment until the code is supplied |
| Scheduled appears in a CR, DCR, PR, or CA family workflow | Stop validation before upload/import. Show: Scheduled status is not supported for change type '{change_type}' (base family '{family}'). Remove Scheduled from the requested workflow before importing. Identify the offending workflow step; do not silently remove it, even when copied unchanged |
| Change Type header Start Date or End Date is requested | Show: Warning: Change Type Start Date and End Date are not supported by the import/export process and will be skipped. Continue with all other supported requested changes. Do not default, derive, add, or invent either header date column. This does not apply to an attachment-category Change Policy association Start Date. |
| Base Change Type is missing or blank during creation | Classify as input validation; stop and show: Base Change Type is missing from your request. Please provide the name or code of the change type to copy before I can create the new change type. Wait for the missing input before preparing or submitting the creation package |
| Missing entities during update | Report missing related rows and return to selected-type dependency validation; retain unchanged dependent rows in the rebuilt package |
| Duplicate Route or route-step identifiers | Report the conflicting copied entities; correct new identifiers and references before rebuilding the creation package |
| EGO_ATTR_DISPLAY_CONFIG_U2 violation | Recheck the target relationship and header-row selection; for child targets remove header-attribute rows while retaining other dependencies |
| Requested child header changes cannot be applied | Disclose the unapplied changes and base-only restriction; do not silently target the base |
| Blank default lookup rejected during validation | Stop before upload; report the validation result and retain the existing type and shared lookup unchanged |
| Attachment category cannot be resolved or is ambiguous | Stop before Change Order Types package preparation; report `status: failed`, `failure_class: catalog_or_metadata_mismatch`, the Category Name, entity `EGO_ENGINEERING_CHANGES_B`, match outcome, and recommended action. Do not substitute a similar category |
| Attachment category creation fails | Stop before Change Order Types package preparation or import; report `status: failed`, the failure class and error returned by Manage Attachment Categories for Product Management, Category Name, entity `EGO_ENGINEERING_CHANGES_B`, and recommended action. Do not create the change order type |
| Requested attachment category lacks a Change Policy association | Stop before import; report `status: failed`, `failure_class: input_validation` or `catalog_or_metadata_mismatch` as applicable, target Change Policy, requested and resolved category identities, and recommended action. Do not create the change order type without the requested association |
| Attachment-category association Start Date cannot be applied | Stop before import; report `status: failed`, `failure_class: input_validation`, target Change Policy, requested category, supplied or defaulted association Start Date, and recommended action. Do not create the change order type without a valid dated association |
| Unknown export mapping or enterprise policy authority | Report the specific unresolved contract; do not invent columns, joins, identifier allocation, or policy evidence |
| Failed import | Stop and report the failure; do not automatically retry the mutation |
| User requests creator removal | Show: Removing a creator from a change type through this import workflow is unsupported. Please remove the creator row in the Change Order Type UI. Retain existing creator rows in packages for other requested changes and report creator removal as not processed, requiring the UI action |
| Export attempt returns no Process ID, ZIP, or process log | Validate or refresh authentication through core.auth.fusion-oauth-authentication, then submit exactly one new read-only EGO_MANAGE_CHANGE_ORDER_TYPES setup-data export through shared.setup-export.task-level-export after active workflow prerequisites pass; capture every available Process ID, ZIP, or process log |
| Authentication validation or refresh fails | Stop before the new export and report the authentication failure through the active workflow |
| Fresh export retry still returns no Process ID, ZIP, or process log | Stop and report a Fusion export-process issue with environment, task code, attempt details, and missing evidence; do not prepare or import stale data or silently submit another retry |
| Export returns a Process ID or log but no usable ZIP | Follow bounded status and log handling for that process through the shared export workflow; stop on failure or timeout and report the evidence; a Process ID or log alone does not permit import preparation |
| Completed import, including Success or Succeeded | Retrieve and review the status, import logs, and available row-level results through the active core.data-loader workflow; reconcile every requested change with the approved package and evidence before reporting completion |
| Successful job with warnings or skipped changes | Report the job status separately from the request outcome; identify processed, partially processed, and not processed requests with the associated warning or error; preserve successful changes and do not automatically retry |
| Missing logs or inconclusive processing evidence | Mark affected requests unverified and explain what evidence is unavailable; do not infer that a successful job processed every request |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Internal workflow-control preparation | Do not announce routine ORA_EGO_WORKFLOW_STATUS_CONTROL deduplication or uniqueness checks in user-facing plans, progress, previews, or summaries. Retain diagnostics; report an actionable failure only when it prevents completion |
| Validation and ZIP preparation | Validation results and any missing inputs; require confirmation only for a constructed Internal Name, as explicitly requested. Do not add other intermediate confirmation gates |
| Attachment-category outcome | When requested, report whether the category was reused or created, its entity `EGO_ENGINEERING_CHANGES_B`, and the validated target Change Policy association with its effective Start Date. On any category, association, or association-date failure, report the failed stage and stop before type import |
| Export outcome and next action | Show the new attempt's available evidence and missing outputs. For a successful fresh ZIP, prepare and validate the import package, show its contents, and request import approval. Otherwise request direction to restart export or resume/restart runbook execution through its recorded workflow state, without automatically replaying completed mutations |
| Before import | Exact target environment, operation, prepared ZIP and its member paths, configuration rows or files to import, and any unapplied user requests |
| Internal package handling | Do not announce routine child-type header-attribute row exclusion in user-facing plans, progress messages, previews, or summaries. Keep the exclusion and its validation internal; disclose only an explicitly requested change that cannot be applied, using the business restriction rather than row-exclusion mechanics |
| Import approval | Obtain explicit approval for the exact displayed ZIP and target through core.data-loader's approval workflow; do not introduce duplicate approval prompts |
| ZIP changed after review | Revalidate, show replacement ZIP contents, and obtain new explicit approval before import |
| Post-import job summary | Environment, target change type, job or process identifier, submitted package reference, and Fusion's reported terminal status |
| Post-import request reconciliation | For each user-requested change: requested value or action, submitted or excluded, processed / partially processed / not processed / unverified outcome, affected entity or row, supporting log reference, warning or error code and message, and next action |
| Request totals | Summarize processed, partially processed, not processed, and unverified requests; identify requests excluded before submission as not submitted and never count retained unchanged dependency rows as completed requests |
| Log retention | Retain the actual downloaded import log file or files alongside the request-outcome summary in a distinct run/job subfolder under the active project's task artifact directory; do not overwrite prior import evidence or substitute a reference for the file. Redact credentials and sensitive payloads before persistence, preserve diagnostic warnings/errors and processing outcomes, and identify redactions |
| Retained evidence links | Link the saved log files from the summary and final response; record the job/process identifier and submitted package reference. If retrieval or persistence fails, disclose the failure and do not claim log retention |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Import approval is absent | Do not import |
| Creator removal requested | Do not prepare or submit a creator-deletion ZIP or omit creator rows to attempt deletion; direct the user to the Change Order Type UI |
| Export retry produces no usable fresh setup-data ZIP | Do not prepare or import from stale data; do not treat a Process ID or log as an importable package |
| Requested attachment category is unresolved, creation failed, its Change Policy association is absent, or the applied association Start Date is blank or invalid | Do not prepare or submit a Change Order Types creation package; do not create the change order type without a valid dated association |
| Package changed after approval | Do not submit using stale approval |
| Execution handoff | Do not substitute direct REST, browser, or another import route for core.data-loader |
| Completed job awaiting log review | Do not declare all requested changes successful based only on the job status |
| Corrective import after a warning or error | Do not automatically resubmit; prepare and validate the correction, show the exact replacement package, and obtain explicit approval through the existing import workflow |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COT.IMPORT_GATE | step | 60 | execution_gate | approved->COT.READY_FOR_HANDOFF;blocked->COT.REPORT_ISSUES | COT.ENFORCE_DESIGN | stop | Package validation is complete and import is requested; return gate results to core.data-loader, not a claim of completed import |
| COT.REPORT_ISSUES | step | 70 | error_handler | reported->COT.STOP | none | stop | A prior node reports an issue or an import failure is returned |
| COT.STOP | terminal | 80 | terminal | none | COT.REPORT_ISSUES | stop | Return issues without importing or retrying |
| COT.READY_FOR_HANDOFF | terminal | 90 | terminal | none | COT.IMPORT_GATE | stop | Return validated approval-gate results to core.data-loader; this is not import completion |
