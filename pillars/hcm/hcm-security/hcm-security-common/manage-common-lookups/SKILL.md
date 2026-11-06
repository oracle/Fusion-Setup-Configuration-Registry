---
skill_id: "hcm.hcm-security.hcm-security-common.manage-common-lookups"
name: "Manage Common Lookups Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Common Lookups under the HCM Security Common functional area."
layer: "pillar"
pillar: "HCM"
offering: "HCM Security"
functional_area: "HCM Security Common"
functional_area_code: "ORA_HCM_SECURITY_COMMON"
task_code: "FND_MANAGE_COMMON_LOOKUPS"
task_name: "Manage Common Lookups"
parent_skill_id: "hcm.hcm-security.hcm-security-common"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "HCM hcm security pillar team"
version: "0.1.0"
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
  - "core.fusion-api.apps-common"
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
    default_location: "project/{project_id}/artifacts/pillars/hcm/hcm-security/hcm-security-common/manage-common-lookups/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/hcm/hcm-security/hcm-security-common/manage-common-lookups/current/"
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

# Manage Common Lookups Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Common Lookups` under `HCM Security Common`.

## Setup Task Skill Contract

- task_code: `FND_MANAGE_COMMON_LOOKUPS`
- task_name: `Manage Common Lookups`
- parent_skill_id: `hcm.hcm-security.hcm-security-common`
- pillar: `HCM`
- offering: `HCM Security`
- functional_area: `HCM Security Common`
- functional_area_code: `ORA_HCM_SECURITY_COMMON`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Common Lookups` under `HCM Security Common`.

## Setup Task Metadata

- Task name: `Manage Common Lookups`
- Task code: `FND_MANAGE_COMMON_LOOKUPS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`

## Apps Common CRUD Routing

The catalog export/import flags remain task metadata. Route every read, create,
edit, and delete request only through `core.fusion-api.apps-common`; do not use
Core Data Loader, FSM import, direct REST payload construction, or an alternate
export/import route.

Require `LookupType`, an explicit operation, and an exact code or meaning.
Resolve the exact lookup type and value before a mutation; use an explicitly
absent legislation scope as global, never as a substitute for a known value.
Preserve unrequested values, preview the exact target and delta, require
explicit approval, invoke the shared capability once, and re-read to reconcile
the outcome. Do not retry an uncertain mutation automatically.

### Lookup Resolution Contract

- Resolve `LookupType` exactly. Use the Apps Common Legislation Code Finder
  semantics with the resolved Lookup Type and an explicit Legislation Code or
  explicit global scope.
- For code-or-meaning resolution, the provider must read the paginated child
  collection `commonLookups/{LookupType}/child/lookupCodes`, rather than using
  `expand=lookupCodes` on the parent resource.
- Request `limit` and `offset` and continue through every page until
  `hasMore=false`. Retain only rows where `EnabledFlag=Y` before matching.
- Match `LookupCode` exactly or `Meaning` case-insensitively. Require exactly
  one match across all pages; return `MISSING` for zero matches and an
  ambiguity failure for multiple matches. Never accept a partial match.
- For create, require unique Lookup Code and Meaning, re-read to prove absence,
  and require approval of the minimal core-owned request before one invocation.
- For edit or delete, re-read the exact current value, accept only explicit
  supported changes, invalidate approval if identity, current state, metadata,
  or fingerprint changes, and prove the requested state with a fresh read.
- Do not construct or persist a task-local REST payload, connected host,
  assembled URL, credentials, or response payload.

Use this task metadata when invoking those skills:

- Offering: `HCM Security`
- Functional area / Setup Object: `HCM Security Common`
- Setup task name: `Manage Common Lookups`
- Setup task code: `FND_MANAGE_COMMON_LOOKUPS`


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

Use the parent functional-area skill `hcm.hcm-security.hcm-security-common` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Provider Routing: Common Applications Lookups

- Provider product/team: Common Applications / ApplCore.
- Provider skill and route: `core.fusion-api.apps-common` through its
  `references/lookups/common-lookups.md` route.
- Consumer dependency: Application Lookup Foundation Skill.
- Invoke the provider to read current lookup state before proposing a configuration change. Keep provider CRUD behavior and setup-task ownership in the provider skill. The provider uses `core.fusion-api.rest-api-client` for the Common Lookups REST request.
- Send only the exact `lookupType` code. Do not send an FSM display name and do not select a lookup subfunction until its lookup-type classification is confirmed.

### Confirmed Public Worker Access lookup types

The Public Worker Access Phase 2 Common Lookup specification confirms the following values for `lookupType`:

- `ORA_PER_PWA_USER_SESSION_ATTR`
- `ORA_PER_SECURITY_CRITERIA`
- `ORA_PER_PWA_TEXT_OPERATOR`
- `ORA_PER_PWA_TEXT_ATTRIBUTE`

For validation, the consumer must also restrict requested codes to the values supported by the selected type. For example, `ORA_PER_PWA_TEXT_OPERATOR` supports `ORA_PER_STARTS_WITH`, `ORA_PER_ENDS_WITH`, and `ORA_PER_CONTAINS`; `ORA_PER_SECURITY_CRITERIA` includes `ORA_SEC_CRIT_WORKER_ATTRIBUTE` and `ORA_SEC_CRIT_UDF` for Public Worker Access.
