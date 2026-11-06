---
skill_id: "cx.configure-price-quote.quoting.oracle-sales-to-quoting-integration"
name: "Configure Oracle Sales to Quoting Integration"
description: "Creates and validates CPQ Integration Center CRM and Generic Integration connections through the registered IntegrationVendors Data Loader business object."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
functional_area: "Quoting"
functional_area_code: "CUSTOM_QUOTING"
task_code: "CUSTOM_ORACLE_SALES_TO_QUOTING_INTEGRATION"
task_name: "Oracle Sales to Quoting Integration"
parent_skill_id: "cx.configure-price-quote.quoting"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "IntegrationVendors"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "CX Configure Price Quote pillar team"
version: "0.2.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fusion_environment_context"
  - "connection_profile"
  - "integration_vendor_values"
  - "active_runbook_context"
  - "user_managed_enablement_confirmation"
  - "execution_approval"
outputs:
  - "integration_vendors_workbook"
  - "data_loader_validation_result"
  - "data_loader_execution_result"
  - "connection_staging_handoff"
  - "cpq_ui_verification_handoff"
  - "diagnostics"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration"
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.runbook"
uses_core:
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/quoting/oracle-sales-to-quoting-integration/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/quoting/oracle-sales-to-quoting-integration/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
side_effects:
  - "Generates and validates local IntegrationVendors Data Loader workbooks and archives from live Fusion metadata."
  - "Uploads and initiates a Data Loader request only through core.data-loader after Task Hook validation and explicit approval."
  - "Opens CPQ Integration Center only for user-managed verification and credential entry."
required_privileges:
  - "Access to the registered IntegrationVendors Data Loader business object."
  - "Privileges to upload and initiate the approved Data Loader archive."
  - "Access to the active Oracle Sales to Quoting Integration Run Book task."
---

# Configure Oracle Sales to Quoting Integration

## Purpose

Configure CPQ Integration Center connections using the registered `IntegrationVendors` Data Loader business object. This task replaces direct CPQ REST calls so authorization, payload validation, archive handling, and execution use the repository-standard Data Loader controls.

## Dependency

When Fusion Sales and CPQ are in scope, invoke `cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration` in its read-only verification path before preparing a connection load. Record its readiness result in the project workspace. Do not use this task to change Fusion Sales instances or actions.

## Preflight

Before generating a source artifact or opening Fusion:

1. Resolve the project workspace and require an active Run Book binding. The selected task must be `Oracle Sales to Quoting Integration` with task code `CUSTOM_ORACLE_SALES_TO_QUOTING_INTEGRATION`.
2. Confirm that the selected Fusion environment matches the active Run Book environment and that `IntegrationVendors` is visible in Data Loader.
3. Treat the active Run Book Fusion environment base URL as the endpoint source for both staged profiles. Do not use a different host unless the user explicitly changes the Run Book environment.
4. Require exactly one connection profile per artifact: `fusion-crm` or `generic-integration`. The standard sequence is CRM staging first, followed by Generic Integration staging only after the user confirms the CRM connection is enabled.
5. Use the literal `FDOS_CREDENTIAL_REQUIRED` for both username and password in a staging artifact. Never place credentials, bearer tokens, or CPQ OAuth-scope values in a workbook, DAT, ZIP, project artifact, diagnostic, or chat response.
6. Set every staged connection's `enabled` item to `false`. Enabling and credential entry are user-managed CPQ UI actions.
7. Stop on an ambiguous Business Object, missing `properties` child, or missing `items` child. Do not reconstruct a direct REST request as a fallback.

## Data Loader source model

Generate the workbook from live `IntegrationVendors` metadata through `core.data-loader`. The artifact must preserve this hierarchy:

```text
IntegrationVendors (integrationVendorsKey)
└── properties (propertyId, integrationVendorsKey)
    └── items (propertyId, name, value)
```

Use a different `integrationVendorsKey` and `propertyId` for each connection. Every `items` row must carry the same `propertyId` as its `properties` parent. The Data Loader metadata column order is authoritative; values must follow the order in that section's `METADATA` line.

### Fusion CRM profile — stage first

Populate the parent with `integrationType=CRM` and `vendorName=fusion`. Populate `items` with:

| Item name | Staged value |
| --- | --- |
| `name` | `FusionSales` |
| `variableName` | `FusionSales` |
| `endPointURI` | Active Run Book Fusion environment base URL |
| `username` | `FDOS_CREDENTIAL_REQUIRED` |
| `password` | `FDOS_CREDENTIAL_REQUIRED` |
| `enabled` | `false` |

After the CRM archive succeeds, stop for the user to enter the real credentials, enable the connection, and save it in **CPQ Admin > Integrations > Integration Center**. Use the declared read-only UI verification step to confirm the enabled state. Do not proceed to Generic Integration staging until the user confirms this step.

### Generic Integration profile — stage second

Populate the parent with `integrationType=genericIntegration` and `vendorName=genericIntegration`. Populate `items` with:

| Item name | Staged value |
| --- | --- |
| `name` | `Fusion Account Integration` |
| `requestUrl` | Active Run Book Fusion environment base URL |
| `username` | `FDOS_CREDENTIAL_REQUIRED` |
| `password` | `FDOS_CREDENTIAL_REQUIRED` |
| `enabled` | `false` |

Use a literal HTTPS URL, not Markdown link syntax. After the archive succeeds, stop again for the user to replace the placeholders, enable the connection, save it, and confirm the enabled state in Integration Center.

## Workflow

1. Generate and validate a **Fusion CRM** XLSX/archive through `core.data-loader` from live `IntegrationVendors` metadata, using the staged CRM values above.
2. Invoke `core.data-loader.task-hook` for the selected Run Book task. Complete its declared read-only validation rules and build the required Data Loader preview. A missing or failed Task Hook envelope blocks upload.
3. Present the exact target environment, immutable CRM archive, `FDOS_CREDENTIAL_REQUIRED` staging values, and `enabled=false`. Upload and initiate only after explicit approval of that exact validated archive.
4. After the CRM initiation is accepted, return the Data Loader initiation result and stop. Do not poll automatically. On a later explicit user request for status, use the `core.data-loader` status workflow. Proceed to CPQ **Admin > Integrations > Integration Center** only after a successful load outcome is confirmed. The user replaces the placeholders, enables the CRM connection, saves, and confirms it is enabled. Do not enter or retain credentials. End this stage with an explicit outcome: either `CRM connection configured and enabled`, or `CRM Data Loader succeeded; user credential and enablement action remains`.
5. Only after that confirmation, generate and validate a separate **Generic Integration** XLSX/archive with the staged Generic values above; repeat Task Hook validation and obtain a new explicit approval for that exact archive.
6. After the Generic initiation is accepted, return the Data Loader initiation result and stop. Do not poll automatically. On a later explicit user request for status, use the `core.data-loader` status workflow. Proceed to user-managed credential entry, enablement, save, and read-only enabled-state confirmation only after a successful load outcome is confirmed. End the skill with an explicit outcome: either `Fusion CRM and Fusion Account Integration connections are configured and enabled`, or the exact remaining user-managed credential or enablement action.

## Approval and security boundaries

- Do not call `/cpq/rest/*/integrationVendors` directly.
- Do not retain or reintroduce scripts that make direct CPQ Integration Vendor GET, POST, or PATCH requests.
- Do not upload or initiate a Data Loader request without the immutable preflight, approved Task Hook envelope, and explicit approval for the exact archive.
- Never retry a live Data Loader initiation, REST mutation, or UI save without a new explicit approval.

## Diagnostics and recovery

Classify failures as `input_validation`, `catalog_mismatch`, `auth_or_authorization`, `transport_or_environment`, `fusion_api`, `process_failed`, `artifact_persistence`, or `approval_blocker`.

- For metadata or hierarchy mismatches, regenerate from live `IntegrationVendors` metadata and revalidate.
- For Task Hook failures, preserve the redacted validation result and stop; resolve the selected Run Book task context before creating another archive.
- When the user explicitly asks for a failed Data Loader request's status or errors, retrieve them through `core.data-loader`; do not issue a compensating direct CPQ REST call.
- Redact credentials, tokens, authorization headers, and sensitive payload values from all workspace artifacts and diagnostics.

## Validation

```bash
python3 core/data-loader/scripts/generate_sample_dat.py --help
python3 core/data-loader/scripts/validate_data_load_file.py --help
python3 -m unittest discover -s core/data-loader/task-hook/tests -v
```
