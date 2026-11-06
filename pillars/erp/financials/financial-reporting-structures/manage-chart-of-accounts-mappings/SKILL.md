---
skill_id: "erp.financials.financial-reporting-structures.manage-chart-of-accounts-mappings"
name: "Manage Chart of Accounts Mappings Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Chart of Accounts Mappings under the Financial Reporting Structures functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Financial Reporting Structures"
functional_area_code: "ORA_ASK_FIN_REPORTING_STRUCT"
task_code: "GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING"
task_name: "Manage Chart of Accounts Mappings"
parent_skill_id: "erp.financials.financial-reporting-structures"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
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
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/financial-reporting-structures/manage-chart-of-accounts-mappings/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/financial-reporting-structures/manage-chart-of-accounts-mappings/current/"
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

# Manage Chart of Accounts Mappings Setup Task Guidance

## Purpose

Build and maintain mappings between one source chart of accounts and one target chart of accounts. Keep mapping headers, segment rules, single-source and multiple-source rollup rules, account rules, hierarchy readiness, overlap analysis, FBDI readiness, and post-implementation review inside this one pillar skill.

## Setup Task Skill Contract

- task_code: `GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING`
- task_name: `Manage Chart of Accounts Mappings`
- parent_skill_id: `erp.financials.financial-reporting-structures`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Financial Reporting Structures`
- functional_area_code: `ORA_ASK_FIN_REPORTING_STRUCT`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- source_catalog: `knowledge/setup-task-catalog/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Chart of Accounts Mappings` under `Financial Reporting Structures`.

Use segment rules for broad mapping logic and account rules for precise exceptions. When both apply to the same source account combination, report the overlap and apply the account rule as the effective result.

## Read Order

1. Read `ora-resource/ora_input_intake.md`.
2. Read `ora-resource/ora_input_validation.md`.
3. Read `ora-resource/ora_dependency_readiness.md`.
4. Read `ora-resource/ora_reference_lookups.md`.
5. Read `ora-resource/ora_defaulting_rules.md`.
6. Read `ora-resource/ora_design_advisory.md`.
7. Read `ora-resource/ora_design_enforcement.md`.
8. Read `ora-resource/ora_bulk_intake.md`.
9. Read `ora-resource/ora_rest_execution.md`.
10. Read `ora-resource/ora_error_handling.md`.

## Setup Task Metadata

- Task name: `Manage Chart of Accounts Mappings`
- Task code: `GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`

## Supported Mapping Activities

- Compare mapping headers by name, source chart of accounts, target chart of accounts, description, security behavior, and child rules.
- Define target-segment rules with Assign single value, Copy value from source, or Use rollup rules.
- Define rollups from one source segment or exactly two source segments.
- Define and review account rules through the supported application workflow.
- Detect account-rule and segment-rule overlaps and state the precedence result.
- Generate FBDI artifacts only for segment and rollup rules.
- Validate hierarchy versions using the intended accounting date.

Do not create child skills for mapping activities.

## Export, Import, and Validation Routing

`CSVExportImportSupportedFlag` is `Y`. Route supported setup-data operations through:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use only the existing FDOS authentication path and core FSM REST client as shared execution primitives. Never store credentials or authorization material.

## Lifecycle

1. Validate business inputs and intended accounting date.
2. Select FSM for standard segment, single-source rollup, and account rules. Obtain a current target-environment template/spec ZIP through shared.setup-export.task-level-export (the default template-only route) whenever needed, independently of mapping inputs, COA resolution, or comparison. Require the Oracle XLSM only for a selected FBDI route.
3. For FSM, follow the Template Contract Review and FSM Package Preparation procedures in ora-resource/ora_reference_lookups.md using the current ZIP and the Reviewed FSM Schema and Reviewed FSM Field Semantics sections in ora-resource/ora_reference_lookups.md. This contract is reference data for source/target semantics and S/C/R methods, not an executable dependency; a populated full-task export is not required. Resolve environment-specific identifiers separately. Stop on incompatible headers or metadata rather than guessing.
4. Validate source and target charts, segments, referenced values, hierarchies, hierarchy versions, and deployment readiness.
5. Find the mapping header using current target-environment evidence and compare its complete requested definition. Template acquisition does not depend on this comparison or on COA resolution. With no current mapping evidence, keep comparison pending and permit local package preparation only; never infer absence from an empty template or another environment's export.
6. Stop on an identical mapping, or show field-level differences and obtain direction for a changed mapping.
7. Validate segment, rollup, multiple-source, and account rules as one parent-and-children design. A create requires an actual rule definition; never submit a header-only smoke test. A segment-rule design must cover every enabled target segment exactly once, using current verified target metadata and valid values.
8. Generate the source mapping, validation result, default-derivation record, and import-readiness record.
9. Preview local preparation separately from submission readiness. A pending comparison terminates at prepared-only; do not route it to Data Loader approval. Require all applicable checks before a live preview.
10. Route every import through core.data-loader and its Task Hook, immutable artifact, and approval workflow. Use Increment by default. Account rules use the verified FSM CSV contract, not FBDI.
11. Check concurrency during preapproval validation for updates. Follow Data Loader's persisted approval-bound artifact procedure after approval; do not rebuild the artifact or duplicate its approval gate.
12. A successful Data Loader initiation is terminal for that request. On a requested result check, verify through its status workflow and the Chart of Accounts Mapping Rules Report or equivalent read-only review.

## Inputs

- `implementation_objective`
- `project_context`
- `mapping_definition`
- `intended_accounting_date`
- `current_fsm_template` (FSM route)
- `current_fbdi_template` (FBDI route only)
- `existing_mapping_evidence`

## Outputs

- `source_mapping`
- `mapping_comparison`
- `mapping_validation_result`
- `default_derivation_record`
- `import_readiness_record`
- `configuration_blueprint`
- `skill_run_record`
- `token_usage_record`

Persist supported implementation artifacts under:

`project/{project_id}/artifacts/pillars/erp/financials/financial-reporting-structures/manage-chart-of-accounts-mappings/current/`

## Refusal Rules

- Do not infer FBDI columns, codes, or defaults from EDM physical columns or UI labels.
- Do not generate account-rule FBDI rows.
- Do not submit a package with unresolved technical values or failed local validation.
- Do not use Replace for a partial package.
- Do not use failed live imports as default discovery.
- Do not perform a mutating Fusion action without explicit approval.
- Do not proceed when the current mapping changed after the comparison baseline.

## FSM Preparation and Evidence

No task-specific executable is required. Use the existing shared task-level exporter, setup-data and reference-data validation workflows, and core.data-loader. Follow the task's explicit procedures in ora-resource/ora_reference_lookups.md for template review, current segment/value evidence, exact-name mapping comparison, and package preparation. The agent evaluates these rules and records the evidence in Task Hook ruleResults before the existing Data Loader preview/approval workflow.

Read the Reviewed FSM Schema and Reviewed FSM Field Semantics sections in ora-resource/ora_reference_lookups.md as the reviewed schema reference. Compare current CSV headers, metadata attribute types, object paths, sequence, and batch names before using their field/code meanings. These sections contain no customer setup rows and do not establish current environment state.

Obtain template/spec exports whenever needed. Obtain current name-scoped mapping evidence separately for duplicate/update checks; templates and foreign or old snapshots cannot establish absence. Both template and data exports can have ProcessType=EXPORT, so retain the originating operation, target environment, scope, timestamp, and artifact fingerprint.

Reject header-only creation, missing target-segment coverage, unverified values, and broken parent-child links before live preview. Preserve string values and leading zeros, leave unwritable audit fields blank, and prepare an immutable ZIP containing only the requested mapping data. Registry readiness means graph validity; package validity and live submission readiness require separate evaluated evidence.

## Existing Skill Refinement Notes

No existing shared or core skill requires a functional change. This skill reuses the current task export, setup-data validation, reference-data validation, task import, authentication, and FSM-client responsibilities without redefining them.
