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
version: "0.1.2"
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
  - "core.data-loader.task-hook"
  - "core.fusion-api.apps-common.profile-options"
  - "core.fusion-api.fsm-rest-client"
  - "core.fusion-api.rest-api-client"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
depends_on:
  - "shared.implementation-planning.fsm-set-optin.fsm-set-optin-features"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
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

`registrationForRecallAlerts` is the catalog-registered REST-mode import business object. The catalog's `N` flags do not establish an FSM CSV route. Use [Data Loader](../../../../../core/data-loader/SKILL.md) and [Task Hook](../../../../../core/data-loader/task-hook/SKILL.md) for an authorized import. Read [execution safety](references/execution-safety.md) before any source preparation, sample generation, or external request. A registered business-object name is not a REST endpoint contract.

1. Bind the selected project, environment, OAuth profile and approved Run Book/task context. Complete the private-source, path, credential-disclosure and operation-routing gates in execution safety before invoking a helper. Resolve the exact registered object and supported create/update operation from authorized target metadata; unknown target families or unsupported Apps Common routes block execution.
2. Let Data Loader validate mapping and live schema and prepare the exact immutable upload artifact. For an import, serialization and persistence occur **before approval**, under the provider's preflight workflow. Keep a populated credential source and every derived artifact in the approved private staging location outside the repository and project; project evidence contains only sanitized facts and digests. Blank samples may use project artifact storage.
3. Use Data Loader's returned persisted preflight and prepared archive for this task's rules. Require exactly one populated registration root in those final bytes. Before showing approval feedback, invoke Task Hook's `data-load` route for the supplied task context, task name and sequence; read its execution guide and the returned rule files, then evaluate the graph in [ora_rule_registry.json](ora-resource/ora_rule_registry.json). Registry readiness means the rules can be evaluated, not that the checks passed. Do not inspect an independently edited source as evidence for the retained artifact.
4. Return ordered, sanitized `ruleResults`, one per planned resource. Use Task Hook's `build-data-load-preview --input-stdin` with `finalData.archiveSha256` bound to the final archive and only the non-sensitive summary fields described in execution safety. A failed input, lookup or design gate stops the load before approval feedback. Do not put registration rows or credential values in the Task Hook preview.
5. Follow Data Loader's own approval workflow exactly once. After its authorized approval, use Task Hook's `approve-data-load-preview` and `verify-approved-data-load-archive` commands. Pass the returned `taskValidationEnvelope` unchanged to Data Loader together with its retained approved preflight. Never construct envelopes, approvals or digest bindings manually. Submit only the exact verified archive through Data Loader; no direct REST registration write is selected by this skill.
6. A later approved submission verifies artifact integrity, environment, Run Book and Task Hook bindings; it does not reopen the original source, refresh metadata, rebuild the archive, or rerun task checks. A correction to the intended data, mapping, target or task rules starts a fresh preflight, Task Hook evaluation and approval. A missing or changed retained artifact/envelope also requires that fresh cycle. A process restart alone does not invalidate intact, verified artifacts. Never replay an uncertain write.

The domain rules remain in [input validation](ora-resource/ora_input_validation.md), [design enforcement](ora-resource/ora_design_enforcement.md), [reference lookups](ora-resource/ora_reference_lookups.md) and [error handling](ora-resource/ora_error_handling.md). The graph blocks import preview until the selected environment's registration count and create/update capability are verified. Required credential fields depend on the selected mail provider and verified operation; sample attribute metadata alone does not establish universal requiredness.

## Validate an Existing Registration

When the user explicitly asks to validate the registration, select the `validateCredentials` REST business object for that validation request. Do not add it to the `registrationForRecallAlerts` import list or run a Data Loader import as a substitute for validation. Oracle's public setup instructions describe the registration's **Validate and Save** action for Microsoft and Google mail clients; they do not establish the `validateCredentials` REST path, HTTP method, request schema, or whether the operation changes state. The nested task graph checks the documented input and design requirements; the business-object name alone is not an executable REST contract.

Before a live validation request, confirm the exact `validateCredentials` operation and payload from current public Oracle REST documentation or the selected environment's authorized REST Describe metadata. Confirm the environment, existing registration identity, required privileges, and any side effects. The current v3 task graph and Task Hook provide validation rules and the Data Loader lifecycle, not a credential-validation REST execution route. Keep live `validateCredentials` execution blocked until a separately reviewed active workflow declares its client, exact operation, payload, privileges, side effects and approval gates. If the operation is not published or cannot be verified, record the missing REST contract as a blocker and stop; do not guess a URL, send credentials to another endpoint, or replace validation with the UI action. Redact the client secret, refresh token, and other credentials from previews, logs, and project artifacts.

Public setup references:

Release check on 2026-11-10: Oracle’s SCM documentation index identifies 26D as current. The equivalent 26D content-curation topic was inaccessible through the documentation lookup; the 26C guide below is an explicitly older-release fallback. Verify target-release metadata before execution. The readiness announcements provide historical feature context.

- [Oracle 26C implementation guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/enable-oracle-content-curation-service.html) (task prerequisites, registration values, pod-unique email, and Validate and Save).
- [Oracle 25A recall alert registration instructions](https://docs.oracle.com/en/cloud/saas/readiness/scm/25a/inv25a/25A-inventory-wn-f35140.htm) (Microsoft mail and Validate and Save).
- [Oracle 25C Google recall alert registration instructions](https://docs.oracle.com/en/cloud/saas/readiness/scm/25c/inv25c/25C-inventory-wn-f38628.htm) (Google mail and Validate and Save).


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Complete the execution-safety gates, and confirm that `registrationForRecallAlerts` is the exact registered Data Loader business object. Generate an unpopulated sample; never populate credentials in a project workbook.
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

Use [Registration golden scenarios](references/golden-scenarios.md) for synthetic input, design, failure, disclosure, and immutable-artifact lifecycle cases. The scenario review checks the task's assisted guidance and declared graph; live credential validation still requires its verified operation contract.
