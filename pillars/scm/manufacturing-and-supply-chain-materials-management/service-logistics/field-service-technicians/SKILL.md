---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics.field-service-technicians"
name: "Field Service Technicians Setup Task Guidance"
description: "Provides task-specific setup guidance for Field Service Technicians under the Service Logistics functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Service Logistics"
functional_area_code: "ORA_RCL"
task_code: "ORA_RCL_FIELD_SERVICE_TECHNICIANS"
task_name: "Field Service Technicians"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "technicianSubinventories"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.8"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.data-loader"
uses_core:
  - "core.data-loader"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/field-service-technicians/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/field-service-technicians/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Uses core.data-loader for registered metadata, sample generation and explicitly requested load status or diagnostics."
  - "Writes only redacted project run and token evidence; no business-record read, mutation preparation, upload or initiation is supported by this task."
required_privileges:
  - "Access to the selected environment and exact registered Data Loader BO metadata/template for samples."
  - "Status/diagnostic requests require access to the retained load request; read access does not authorize a mutation."

---

# Field Service Technicians Setup Task Guidance

## Purpose

Provide task-specific planning, domain validation requirements and supported Data Loader metadata/sample and status routing for Field Service Technicians. Use the parent Service Logistics skill for functional-area scope. This task does not own cross-task orchestration.

## Setup Task Metadata

- Task: `ORA_RCL_FIELD_SERVICE_TECHNICIANS` / Field Service Technicians.
- Business Object: `technicianSubinventories`.
- Offering: Manufacturing and Supply Chain Materials Management.
- Functional area: Service Logistics (`ORA_RCL`); pillar: SCM.
- Availability, export/import and CSV support flags: Y, as generated from the effective catalog.
- Data Loader import mode: REST. Catalog support does not establish local execution capability.

## Read Order

1. `core/data-loader/SKILL.md` and its required references for the supported operation.
2. `ora-resource/ora_input_validation.md`.
3. `ora-resource/ora_reference_lookups.md`.
4. `ora-resource/ora_error_handling.md`.
5. The task registry and execution plan when evaluating task validation; use Task Hook only through core Data Loader's declared workflow.

## Current Capability Status

No complete business/reference reader is implemented or selected by core.data-loader for this task in this checkout. Business-record reads, identity resolution, saved-record verification and all create/update/delete preparation are **unsupported**. Stop with `catalog_or_metadata_mismatch` before authentication, reference retrieval, source preparation, Task Hook preview, approval, upload or initiation for those requests. Report the task, selected environment, requested operation, missing capability and next action. Do not call an absent script or reference guide.

The next action is a separately reviewed core Data Loader reader implementation with environment binding, registration/live-field checks, complete bounded pagination, identity integrity, redaction and tests, followed by task-specific integration. Availability of a new file alone does not enable this workflow; update and review the task's capability gates first. Approval cannot waive the gap. A direct REST client, browser, exporter, samples, historic observations or caller-provided reference lists cannot substitute for that capability.

## Operation Routing and Capability Gates

| Requested operation | Owning route | Current gate |
|---|---|---|
| Inspect metadata or generate a sample | core.data-loader metadata/sample workflow | Exact BO registration, environment, trusted authentication, readable template and safe private output path |
| Read business records or resolve references | Unsupported capability | Stop before external activity; complete task-selected reader is absent |
| Create, update, repair or delete records | Unsupported capability | Stop before source preparation; authoritative identity/reference evidence cannot be obtained |
| Verify saved record values or absence | Unsupported capability | Report verification unavailable separately from load status |
| Monitor or diagnose an existing submitted load | core.data-loader status/information workflow | Explicit request, retained request identifier, matching environment and read privileges |
| Export task data or publish/repair registration | Unsupported capability | No task-selected Data Loader adapter; request separately governed owner action |

## CSV Export, Import, and Validation Workflow

Preserve the generated Y support flags and REST import mode. They describe catalog support. CSV import, export and identity-dependent validation remain subject to the unsupported operation gates above. Local structural/design review can identify missing inputs but cannot establish current Fusion identities or authorize an import.

## Reference Read Workflow

This is a capability stop, not a live read route. Do not obtain business/reference data or execute the task's local identity resolvers for preparation in the current checkout. Stop before preparation and record only redacted capability diagnostics. The reviewed domain requirements below become prerequisites only after a supported reader and task integration are delivered.

Assignments require a verified TechSubinventoryId; creation requires independently resolved PartyId and StockLocationId, duplicate checks and default-usable prerequisite evidence. EnabledFlag-only updates, default usable repair and selected deletion require complete current assignment/reference evidence and independently verified data visibility. The task-local resources retain these domain requirements for future integration; they do not supply evidence or enable execution.

## Data Loader Sample Preparation

After the supported metadata preflight, use `core/data-loader/scripts/generate_sample_dat.py` with exact BO `technicianSubinventories` and a private writable output directory. Keep the editable, attribute-details and key-fields workbooks together. A sample or first-record enrichment is not complete identity/reference evidence and never enables preparation or submission. Keep any customer values outside tracked files and project workspaces.

## Preflight and Failure Handling

Check project/task/catalog identity, requested operation and current capability **before external activity**. Unsupported operations stop immediately with the capability diagnostic above. For supported metadata/sample or explicitly requested status operations, let core validate the selected environment, authentication, registration or request identity, privileges and safe paths.

Use core's failure taxonomy, once-only eligible cached-token recovery, bounded request/polling timeout, process-log retrieval, redaction and no-replay rules. Load its relevant policies before execution. On timeout report environment, operation, task, request identifier when available, last status, elapsed wait and next-check action. Failed or partial diagnostics must retain a failure status; do not infer success from partial data or retry a mutation.

## Data Loader Results

For an explicit status/results request on a previously submitted load, call only core's selected status workflow using the retained request identifier. Return its full report and distinguish load status from verified business values. Do not initiate another load, poll automatically after a different request, or report source values/job counts as current saved records. Saved-record verification remains unsupported under the current capability gate.

## Evidence and Redaction

Persist only sanitized environment, task, operation, capability/failure status, counts, external request references, artifact references, next action and token estimates under the declared project locations. Never persist credentials, tokens, customer rows, sensitive responses or source values in tracked files or project artifacts. Keep permitted source records in memory or private ignored staging outside project/. Record durable run/token evidence according to this manifest.
