---
task_code: "ORA_SVC_MANAGE_SERVICE_REQUEST_ASSIGNMENT_OBJECTS"
task_name: "Manage Service Assignment Objects"
parent_skill_id: "cx.service.communication-channels"
pillar: "CX"
offering: "Service"
functional_area: "Communication Channels"
functional_area_code: "ORA_SVC_COMM_CHANNELS"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
execution_blocker: "Advisory only; task-specific execution contract is unavailable."
---

# Manage Service Assignment Objects

## Scope: Advisory Only

This repository entry supports catalog identification and requirements planning
only. It does not implement validation, export, package preparation, preview,
import or configuration execution for `ORA_SVC_MANAGE_SERVICE_REQUEST_ASSIGNMENT_OBJECTS`.

The effective Fusion catalog marks this task available and export/import/CSV
supported (`Y`). These are catalog facts, not an FSCR execution contract. No Data
Loader import mode is selected by this skill. The local rule registry is still
incomplete and the canonical resolver must refuse execution. The descriptive
execution_blocker metadata is not a substitute for that runtime refusal.

## Advisory Workflow

1. Record the requested business objective, task code, Service offering,
   Communication Channels area, selected project and environment as supplied.
2. Identify the missing task-specific source contract and required evidence;
   do not infer payload fields, keys, defaults or execution steps from another
   task or from catalog support flags.
3. Return `status: blocked`, `stage: capability_readiness`, failure class
   `catalog_or_metadata_mismatch`, this task code and the recommended next action
   through the owning project workflow. Retain sanitized diagnostics and any
   existing artifact references. This local guidance makes no Fusion call.
4. Obtain source-backed task guidance through the resource-authoring workflow,
   compile/review the complete rules and rerun readiness and merge checks before
   proposing this task as executable. No approval or readiness waiver can fill
   the missing contract.

## Execution Boundary

Stop before invoking Data Loader, Task Hook preview, task export/import, REST,
UI/browser automation or another substitute route for this task. Do not create
an import package or treat this advisory entry as an implementation-ready task.
Leave the existing incomplete rule registry intact so direct resolution remains
fail-closed. Do not relabel its TBD rules as ready or bypass the resolver.

## Catalog Identity

- Task: `Manage Service Assignment Objects`
- Task code: `ORA_SVC_MANAGE_SERVICE_REQUEST_ASSIGNMENT_OBJECTS`
- Offering: `Service`
- Functional area: `Communication Channels`
- Available / export-import / CSV flags: `Y / Y / Y` (catalog only)
- FSCR capability: advisory planning only; execution unsupported
- Data Loader import mode: not selected
