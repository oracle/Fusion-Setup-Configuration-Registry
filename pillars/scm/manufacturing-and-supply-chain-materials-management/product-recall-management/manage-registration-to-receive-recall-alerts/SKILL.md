---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.product-recall-management.manage-registration-to-receive-recall-alerts"
name: "Manage Registration to Receive Recall Alerts Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Registration to Receive Recall Alerts under the Product Recall Management functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Product Recall Management"
functional_area_code: "ORA_ENQ_PRODUCT_RECALL_MANAGEMENT"
task_code: "ORA_MANAGE_REGISTRATION_TO_RECEIVE_RECALL_ALERTS"
task_name: "Manage Registration to Receive Recall Alerts"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.product-recall-management"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "registrationForRecallAlerts"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.1"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/product-recall-management/manage-registration-to-receive-recall-alerts/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/product-recall-management/manage-registration-to-receive-recall-alerts/current/"
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
side_effects: []
required_privileges: []
---

# Manage Registration to Receive Recall Alerts Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Registration to Receive Recall Alerts` under `Product Recall Management`.

## Setup Task Skill Contract

- task_code: `ORA_MANAGE_REGISTRATION_TO_RECEIVE_RECALL_ALERTS`
- task_name: `Manage Registration to Receive Recall Alerts`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.product-recall-management`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Product Recall Management`
- functional_area_code: `ORA_ENQ_PRODUCT_RECALL_MANAGEMENT`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObject: `registrationForRecallAlerts`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Registration to Receive Recall Alerts` under `Product Recall Management`.

## Setup Task Metadata

- Task name: `Manage Registration to Receive Recall Alerts`
- Task code: `ORA_MANAGE_REGISTRATION_TO_RECEIVE_RECALL_ALERTS`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Object: `registrationForRecallAlerts`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.

## Registered Data Loader Route

`registrationForRecallAlerts` is the REST-mode setup-data import business object for this task. The catalog's `N` export/import flags do not establish a task-level FSM CSV route. For a request to load this registered business object, use `core.data-loader` for live schema validation, captured session records/native sources, Task Hook validation, and its in-memory preview and approval workflow. Do not invoke a direct REST import or setup CSV route.

The nested validation rules are in [ora-resource/ora_input_validation.md](ora-resource/ora_input_validation.md), [ora-resource/ora_design_enforcement.md](ora-resource/ora_design_enforcement.md), and their compiled [ora_rule_registry.json](ora-resource/ora_rule_registry.json). The registration source must contain exactly one root record. The task graph blocks import preview until the selected environment's current registration count and create or update capability are verified. At the Data Loader session's `awaiting_task_rules` event, Task Hook must evaluate these rules against the returned captured records/native sources. Do not reread the original XLSX, DAT, CSV, or ZIP files or generate a validation DAT/ZIP. Keep rule results, the execution plan, preview, and approval in the same live process; return the ordered rule results through that session. Data Loader serializes generated DAT/ZIP only after approval and preserves captured native formats.

For any correction to source data, target, mapping, or task rules, cancel the pending session and start a new validation session with the corrected inputs. Editing a source file does not change captured data. A lost or expired session requires a fresh session and approval; never reuse a saved preview or approval. Sample generation remains the separate explicit deliverable workflow below.

The source may contain `ClientSecret` for an explicitly requested test. Keep populated credentials outside tracked repository files and `project/{project_id}`. Use a private source location, exclude credential values from previews and diagnostics, and leave the required-field decision to the test requirements and live Fusion validation; the sample's attribute metadata does not mark `ClientSecret` universally required.

## Validate an Existing Registration

When the user explicitly asks to validate the registration, select the `validateCredentials` REST business object for that validation request. Do not add it to the `registrationForRecallAlerts` import list or run a Data Loader import as a substitute for validation. Oracle's public setup instructions describe the registration's **Validate and Save** action for Microsoft and Google mail clients; they do not establish the `validateCredentials` REST path, HTTP method, request schema, or whether the operation changes state. The nested task graph checks the documented input and design requirements; the business-object name alone is not an executable REST contract.

Before a live validation request, confirm the exact `validateCredentials` operation and payload from current public Oracle REST documentation or the selected environment's authorized REST Describe metadata. Confirm the environment, existing registration identity, required privileges, and any side effects. Route the operation through the task's declared Task Hook REST path and shared Fusion REST client only after that path and its preflight contract are documented. If the operation is not published or cannot be verified, record the missing REST contract as a blocker and stop; do not guess a URL, send credentials to another endpoint, or replace validation with the UI action. Redact the client secret, refresh token, and other credentials from previews, logs, and project artifacts.

Public setup references:

- [Oracle 26C implementation guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/enable-oracle-content-curation-service.html) (task prerequisites, registration values, pod-unique email, and Validate and Save).
- [Oracle 25A recall alert registration instructions](https://docs.oracle.com/en/cloud/saas/readiness/scm/25a/inv25a/25A-inventory-wn-f35140.htm) (Microsoft mail and Validate and Save).
- [Oracle 25C Google recall alert registration instructions](https://docs.oracle.com/en/cloud/saas/readiness/scm/25c/inv25c/25C-inventory-wn-f38628.htm) (Google mail and Validate and Save).


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `registrationForRecallAlerts` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "registrationForRecallAlerts" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.product-recall-management` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Review Evidence

Use [Registration golden scenarios](references/golden-scenarios.md) for synthetic input, design, failure, disclosure, and captured-source lifecycle cases. The scenario review checks the task's assisted guidance and declared graph; live credential validation still requires its verified operation contract.
