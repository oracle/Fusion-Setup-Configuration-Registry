---
skill_id: "scm.procurement.purchasing-foundation.manage-buyer-assignment-rule-sets-lookup"
name: "Manage Buyer Assignment Rule Sets Lookup Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Buyer Assignment Rule Sets Lookup under the Purchasing Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Purchasing Foundation"
functional_area_code: "ORA_PO_PURCHASING_FOUNDATION"
task_code: "ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP"
task_name: "Manage Buyer Assignment Rule Sets Lookup"
parent_skill_id: "scm.procurement.purchasing-foundation"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "rule_set"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.fusion-api.apps-common"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.apps-common"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-buyer-assignment-rule-sets-lookup/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-buyer-assignment-rule-sets-lookup/current/"
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

# Manage Buyer Assignment Rule Sets Lookup Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Buyer Assignment Rule Sets Lookup` under `Purchasing Foundation`.

## Setup Task Skill Contract

- task_code: `ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP`
- task_name: `Manage Buyer Assignment Rule Sets Lookup`
- parent_skill_id: `scm.procurement.purchasing-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Purchasing Foundation`
- functional_area_code: `ORA_PO_PURCHASING_FOUNDATION`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Buyer Assignment Rule Sets Lookup` under `Purchasing Foundation`.

## Setup Task Metadata

- Task name: `Manage Buyer Assignment Rule Sets Lookup`
- Task code: `ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Buyer Assignment Rule Set Lookup Routing

Route every lookup-code read or change through `core.fusion-api.apps-common`.
The core skill must select its **Lookups** workflow and the **Standard lookup**
view; do not call a lookup REST endpoint directly from this task skill.

- Lookup type is fixed to `PO_BUYER_ASSIGN_RULE_SETS`.
- Require **Rule Set** (`rule_set`) from the user. It is the only required
  code-level input. Set `LookupCode` to the supplied Rule Set value; do not ask
  the user to provide Lookup Code separately. Accept legacy `lookup_code` input
  as an alias; stop for clarification if both inputs are supplied and differ.
- If omitted, default `Meaning` and `Description` to the supplied `LookupCode`.
- If omitted, default `EnabledFlag` to `Y` and `StartDateActive` to the
  client-local date on which the payload is built, in `YYYY-MM-DD` form.
- Preserve explicitly supplied `Meaning`, `Description`, `EnabledFlag`, or
  `StartDateActive` values. Do not infer an end date, display sequence, tag, or
  any flexfield value.

For example, on 2026-10-23, a request with **Rule Set** = `FSCR2` produces this
default payload:

```json
{
  "LookupCode": "FSCR2",
  "Meaning": "FSCR2",
  "Description": "FSCR2",
  "EnabledFlag": "Y",
  "StartDateActive": "2026-10-23"
}
```

Before a create, the selected core workflow reads
`PO_BUYER_ASSIGN_RULE_SETS` and checks the requested `LookupCode`. It must
stop for an existing code, an ambiguous result, an unavailable lookup type, or
an authorization failure. Present the exact target environment and final
payload for approval immediately before the core workflow performs its create
or update; do not retry a mutation automatically.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Route lookup-code management through `core.fusion-api.apps-common` as
   described in Buyer Assignment Rule Set Lookup Routing.
2. Export setup task data with `shared.setup-export.task-level-export` when an
   FSM baseline is required.
3. Validate setup task data with `shared.validation.setup-data-validator`.
4. Validate reference data with `shared.validation.reference-data-validator`.
5. Import a validated FSM task-export artifact with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Purchasing Foundation`
- Setup task name: `Manage Buyer Assignment Rule Sets Lookup`
- Setup task code: `ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP`

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `rule_set` — user-facing **Rule Set**; mapped to `LookupCode` before defaulting

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.procurement.purchasing-foundation` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
