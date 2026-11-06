---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.intrastat-reporting.intrastat-country-characteristics"
name: "Intrastat Country Characteristics Setup Task Guidance"
description: "Provides task-specific setup guidance for Intrastat Country Characteristics under the Intrastat Reporting functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Intrastat Reporting"
functional_area_code: "JMF_INTRASTAT"
task_code: "ORA_INTRASTAT_COUNTRY_CHARACTERISTICS"
task_name: "Intrastat Country Characteristics"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.intrastat-reporting"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "intrastatCountryChars"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.3"
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
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "core.data-loader"
uses_core:
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/intrastat-reporting/intrastat-country-characteristics/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/intrastat-reporting/intrastat-country-characteristics/current/"
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

# Intrastat Country Characteristics Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Intrastat Country Characteristics` under `Intrastat Reporting`.

## Task Metadata

The manifest above is the authoritative source for task identity, catalog flags,
Data Loader routing, inputs, outputs, dependencies, and workspace persistence.
Use those values when invoking the delegated skills below.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Use REST by default with `intrastatCountryChars`. Use CSV Import only when it is explicitly requested or a native FSM archive is supplied.
2. Request the applicable sample or template through `core.data-loader`; do not create a substitute source or schema in this task guidance.
3. Map the supplied values into that generated source as described below, then continue in the selected Data Loader workflow.

## Download Fusion Data Loader Sample

When an editable sample is needed, request it from `core.data-loader` for the manifest's `intrastatCountryChars` business object. Use the generated workbook headers as the source contract.

## Map Supplied Values to the Generated Sample

After the Data Loader sample or FSM template is generated, populate only the
matching generated columns. Keep user-supplied values unchanged and leave
unspecified generated columns blank. Do not infer values or introduce aliases.

| Supplied field | Generated column |
|---|---|
| TerritoryCode | TerritoryCode |
| CatalogCode | CatalogCode |
| ReferencePeriodRule | ReferencePeriodRule |
| ReportingCurrencyCode | ReportingCurrencyCode |
| ConversionType | ConversionType |
| UnitOfMeasure | UnitOfMeasure |
| CurrencyRoundingMethod | CurrencyRoundingMethod |
| WeightRoundingMethod | WeightRoundingMethod |
| TriangulationMode | TriangulationMode |
| ReturnsProcessing | ReturnsProcessing |
| KitMethod | KitMethod |
| ArrDescriptionReqFlag | ArrDescriptionReqFlag |
| DisDescriptionReqFlag | DisDescriptionReqFlag |
| ArrDeliveryTermReqFlag | ArrDeliveryTermReqFlag |
| ArrTransportModeReqFlag | ArrTransportModeReqFlag |

If a requested field has no matching generated column, stop and obtain the
appropriate Data Loader sample or template rather than modifying the generated
source contract.

## Implementation Notes

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.intrastat-reporting` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
