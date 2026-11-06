---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data.smart-operations-configurations"
name: "Smart Operations Configurations Setup Task Guidance"
description: "Provides task-specific setup guidance for Smart Operations Configurations under the Manufacturing Master Data functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Manufacturing Master Data"
functional_area_code: "ORA_WIS_COMMON_MFG_WORK_SETUP"
task_code: "ORA_WIE_SMART_OPERATIONS_CONFIGURATIONS"
task_name: "Smart Operations Configurations"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
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
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/smart-operations-configurations/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/smart-operations-configurations/current/"
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
    - "26.10"
side_effects: []
required_privileges: []
---

# Smart Operations Configurations Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Smart Operations Configurations` under `Manufacturing Master Data`.

## Setup Task Skill Contract

- task_code: `ORA_WIE_SMART_OPERATIONS_CONFIGURATIONS`
- task_name: `Smart Operations Configurations`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Manufacturing Master Data`
- functional_area_code: `ORA_WIS_COMMON_MFG_WORK_SETUP`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Smart Operations Configurations` under `Manufacturing Master Data`.

## Release Applicability

This task skill is the 26.10 drop2 backport of the reviewed Smart Operations
Configurations skill delivered in 27A merge request 1953. Use the operator's
approved 26.10 target, source revision and delivery instructions for a new run.
Use the [Smart Operations Configurations FSCR guide](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452541)
for supporting procedures. Keep environment-specific results in the selected
project's run records and review reports.

Confirm the selected target's installed release/build, patch, permissions, task
definitions, template and prerequisite data before execution. A source-branch
label, successful sign-in, task catalog flags or historical import does not
establish those facts. Results from another task, release or environment do not
establish readiness for the selected run.

For 26.10, follow the selected Data Loader's immutable upload artifact,
persisted preflight and Task Hook preview/approval workflow. Complete read-only
task validation before preview and approval. Task rules return findings; the
Data Loader owns approval and submission of the retained approved bytes.
After later approval, follow its approved-artifact verification instructions
without reopening original sources or rerunning task validation. Do not use
27A's in-memory session protocol for this backport.

Keep native FSM and Run Book/Data Loader results separate. This applicability
declaration authorizes no Fusion operation, registration, import or Run Book
change and does not itself enforce a release check in the shared planner.

## Setup Task Metadata

- Task name: `Smart Operations Configurations`
- Task code: `ORA_WIE_SMART_OPERATIONS_CONFIGURATIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Source References

This skill supports [FMFG-121484](https://jira.oraclecorp.com/jira/browse/FMFG-121484).
Use the [Smart Operations Configurations parent guidance](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452541)
and [Smart Operations Configurations demo](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452542)
as source references. Retain environment identities, dated export and import
results, and saved-value comparisons in project records and review reports.

## Scoped Preparation and Reviewer Handoffs

1. The configuration-package author obtains a fresh template for this exact
   task through the selected export workflow. Retain the complete
   CSV set and `ASM_SETUP_CSV_METADATA.xml` together, with the task identity,
   source environment, and retrieval date in the approved project records.
   Use that template's actual columns and metadata; do not recreate headers
   from an older package or infer an endpoint from a CSV filename.
2. The configuration-package author maps approved business values to the
   fresh template. Separate organization-level production execution
   parameters, work-center parameters, shared workstation reason codes, and
   reason-code translations. Shared reason rows are not organization-local;
   an organization filter must not omit or clone them. Preserve the fresh
   template's identifiers, relationships, and translation requirements.
3. A second reviewer checks the intended organization and work-center scope,
   every proposed value, shared reasons and translations, missing or
   duplicate keys, and package membership against the approved requirements
   and fresh metadata. Missing values or ambiguous mapping stop preparation;
   an empty export must never supply a default. Compare stored values,
   units, language codes and translations against the approved requirements
   and current metadata. Any translation or metadata correction requires its
   own confirmed source and approval.
4. The author hands the reviewed immutable ZIP and the review findings to the
   Fusion administrator or the explicitly selected Run Book/Data Loader
   operator. The operator confirms the exact environment, task code, final
   archive, applicable privileges, and workflow approval. Changing any CSV,
   mapping, metadata, or ZIP restarts validation and review.

Do not persist customer configuration or credentials in reusable skill source.
This skill defines domain rules and delegates execution to the selected
shared and core workflows. FMFG-121484 calls for local verification, a retained
skill-run record and reviewed source evidence. Apply task-local rules through
the selected shared and core workflows for an approved current run. The story
does not explicitly require a separate skill self-audit. The generated manifest
and records from earlier runs alone do not establish readiness or completion for a new
skill run.

## CSV Package and Task Validation Scope

`CSVExportImportSupportedFlag` is `Y`. The package contains organization-level
parameters, work-center parameters, shared reason codes and reason-code
translations. Apply the task resources to its approved values, reference
identities, relationships and complete template membership.

Use this task metadata for the selected workflow:

- Offering: `Manufacturing and Supply Chain Materials Management`
- Functional area / Setup Object: `Manufacturing Master Data`
- Setup task name: `Smart Operations Configurations`
- Setup task code: `ORA_WIE_SMART_OPERATIONS_CONFIGURATIONS`

### FSM Task CSV Import

Keep `dataloader_import_mode: FSM` for the task CSV package. The author
hands the reviewed ZIP to the Fusion administrator for the separately approved
Data Loader import. Retain `businessObject: ""`; this task has no established
REST business object. Do not invoke an import helper or writable Fusion
endpoint directly from this pillar skill.

### Separate Run Book / Data Loader Path

For an explicitly selected Run Book path, hand the same reviewed FSM ZIP
and its task identity to the Run Book operator. A Run Book invocation does not
change this task to REST mode. Any separate REST mode requires a verified,
registered business object selected by the developer; none is supplied here.
This task provides no Run Book or Data Loader API calls or import retries.

Accepted submission alone cannot establish a successful import or task
completion. Keep the actual import outcome, saved-value comparison and any
separately approved Run Book task change distinct.

## Failure and Recovery Boundaries

- Fail before submission on invalid or missing values, unreviewed mappings,
  stale or mismatched task metadata, missing package members, or an
  unidentified target environment. Record the specific input or metadata
  finding for correction by the author and second reviewer.
- Report received technical errors without inventing retry limits, status
  keys or REST attributes. Use the selected Data Loader instructions for recovery.
- Never repeat a state-changing import, upload, or Run Book update merely
  because its outcome is unknown. Resolve status through the selected
  workflow; obtain any retry approval that workflow requires.
- Follow the current Data Loader output policy for any task records. Never
  copy token caches, secrets or sensitive payloads into reusable skill source.

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

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
