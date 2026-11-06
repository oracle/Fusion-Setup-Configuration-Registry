# Error Handling

## Error Handling Rules

| Condition | Handling |
|---|---|
| FSM template or baseline export is requested | Capture the export request, returned `ProcessId`, every poll result, terminal status, and the downloaded ZIP or process log path. Do not report export success or failure without these artifacts. |
| FSM export fails or times out | Show the terminal status or timeout condition, the `ProcessId`, and the process log path when available. Do not fabricate a package path. |
| Prepared package fails setup-data validation | Stop before approval and show the sanitized validation failures tied to file, row, column, and rule when available. |
| Prepared package fails reference-data validation | Stop before approval and show the sanitized missing or invalid referenced setup values. |
| User approval is missing or incomplete | Stop before upload and request approval that names the target environment, ZIP path, SHA-256, validation results, Data Loader approval preview, and intended operation. |
| FSM import is initiated | Capture and preserve the approved ZIP path, SHA-256, Data Loader approval preview, upload evidence, initiation response, returned request or process identifier, and supplied archive name. Status monitoring must use that returned identifier. |
| FSM import rejects the supplied OrganizationCode as an invalid value | Show the exact sanitized import error and ask the user for a corrected `OrganizationCode`. Do not infer, resolve, or overwrite a replacement code. |
| FSM import fails or times out | Show the returned identifier, terminal status or timeout condition, and process log path when available. Do not retry automatically. |
| FSM import has an uncertain outcome | Do not replay the import. Reconcile with the captured request or process identifier before any further write. |
| Required execution evidence is absent | Stop with a tracking-failure result; do not claim success, failure, or indeterminate business outcome. |

## Error Classifications

| Classification | Trigger | User-facing result |
|---|---|---|
| Missing input | Required environment, task identity, package, operation, or `OrganizationCode` is absent | Ask for the missing value before execution |
| Validation | Setup data or referenced setup values fail validation | Show sanitized validation details and request corrected source data |
| Approval | Exact package, SHA-256, environment, operation, validation result, or Data Loader approval preview is not approved | Stop before upload and request explicit approval |
| Privilege | The Fusion user lacks the privileges needed for FSM setup-data export or import | Show the sanitized privilege failure and required action |
| Process failed | FSM export or import reaches a terminal failed status | Show identifier, status, and process log path when available |
| Tracking | Process identifier, response, status, ZIP, or process log evidence is missing | Stop with an execution-tracking defect |

## Required Disclosure

| Event | Required disclosure |
|---|---|
| FSM template or baseline export | Request summary, `ProcessId`, poll results, terminal status, and ZIP or process log artifact path |
| Package validation failure | File, row, column, rule, and sanitized message when available |
| FSM import initiation | Archive name, approved ZIP path, SHA-256, Data Loader approval preview, upload evidence, initiation status, and returned request or process identifier |
| FSM import failure or timeout | Returned identifier, terminal status or timeout condition, sanitized error details, and process log path when available |
| Tracking failure | Missing evidence field and the reason no business outcome can be reported |

## Refusal Rules

| Context | Refuse or stop when asked to |
|---|---|
| Missing approval | Upload or import a package without explicit approval of the exact ZIP, SHA-256, environment, validation results, Data Loader approval preview, and operation |
| Missing or failed validation | Import a package before setup-data and reference-data validation have passed |
| Missing OrganizationCode | Infer, default, or replace `OrganizationCode` |
| Uncertain import outcome | Replay an import before reconciling the captured process identifier |
| Missing privilege | Execute FSM export or import without the required privileges |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| POR.READY_FOR_APPROVED_FSM_IMPORT | terminal | 4 | terminal | none | POR.ENFORCE_FSM_IMPORT_RULES | stop | Import |
| POR.READY_FOR_FSM_EXPORT | terminal | 5 | terminal | none | POR.VALIDATE_FSM_PACKAGE | stop | Export |
| POR.BLOCKED | terminal | 6 | terminal | none | none | stop | All task operations |
