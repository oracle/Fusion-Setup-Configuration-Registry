---
skill_id: "erp.financials.expenses.manage-tax-fields"
name: "Manage Tax Fields Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Tax Fields under the Expenses functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
task_code: "EXM_MANAGE_TAX_FIELDS"
task_name: "Manage Tax Fields"
parent_skill_id: "erp.financials.expenses"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.5.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "nonproduction_alias_qualification_scope"
  - "ebs_profile_csv_and_source_bound_decisions (optional)"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
  - "alias_qualification_candidate"
  - "alias_readback_comparison"
  - "ebs_tax_candidate_review (when EBS switch-only input supplied)"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-tax-fields/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-tax-fields/current/"
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
  - "May write a local EBS switch-only candidate and review report, with token-usage tracking; never uploads or approves it."
  - "The selected qualification workflow may write a local candidate ZIP under the current project's artifacts directory; it never submits the candidate or certifies a live result."
required_privileges: []
---

# Manage Tax Fields Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Tax Fields` under `Expenses`.

## Setup Task Skill Contract

- task_code: `EXM_MANAGE_TAX_FIELDS`
- task_name: `Manage Tax Fields`
- parent_skill_id: `erp.financials.expenses`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Expenses`
- functional_area_code: `FIN_EXPENSES_DEPLOYED`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Tax Fields` under `Expenses`.

## Setup Task Metadata

- Task name: `Manage Tax Fields`
- Task code: `EXM_MANAGE_TAX_FIELDS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Expenses`
- Setup task name: `Manage Tax Fields`
- Setup task code: `EXM_MANAGE_TAX_FIELDS`




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

Use the parent functional-area skill `erp.financials.expenses` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Evidence-based task workflow

For EBS profile data, use the parent [profile intake](../references/ebs-profile-migration.md)
before this task and then read [EBS Tax handoff](references/ebs-profile-intake.md).
That route asks for missing BU scope and tax-field behavior, retains unknown
profiles for research/exclusion, and separates user intent from technical mapping
and import approval. `scripts/ebs_tax_candidate.py` rebuilds source-bound intent,
omits already-satisfied switches, reuses the existing alias helper for named-BU
creates, and exposes a controlled standalone N-to-Y qualification branch.
It does not expand the maintained live-qualified profile. Explicit tax-rule
requests still use the existing workbook and staged-rule workflow.

This assisted skill defines explicit-value create/update preparation. The former
single populated setup-option alias did not reliably persist ENABLE_TAX in the
tester-reported run. A named-BU ENABLE_TAX=Y create now has
[live qualification](references/option-alias-qualification.md#live-qualified-boundary--2026-10-29)
on the explicitly listed release/schema combinations. An existing-row N-to-Y
update combined with a same-BU US rule create also has
[live qualification](references/option-alias-qualification.md#live-qualified-update-boundary--2026-11-02)
for its recorded release/schema and exact rule values. Use the maintained
profile and local helper for either boundary without asking an extra
qualification-choice question. Other switch operations require explicit
controlled qualification; do not infer broader coverage from these profiles.
For a new named-BU Y switch and new tax rules, automatically plan the
[two-stage create route](references/option-alias-qualification.md#staged-switch-and-tax-rule-creates)
using the qualified switch-only import followed by a rule-only import. This
requires no new qualification choice and does not claim combined-import evidence.
Keep the full requested outcome visible; each stage has its own core approval.
The [alias qualification contract](references/option-alias-qualification.md)
defines identical minimal option aliases, core approval and full readback checks.
Tax-rule-only preparation
keeps both setup-option aliases header-only. Catalog support, target preflight,
candidate validation and Data Loader approval remain required. Selected earlier
scenarios have live evidence; see the dated
[coverage summary](references/evidence.md#validation-coverage--2026-10-07).

For a user-supplied test workbook, read the [setup runbook](references/setup-runbook.md) before preparing a candidate. It defines workbook mappings, missing-input handling, execution prerequisites and evidence needed to close the remaining gaps. It does not waive the executable ora-resource gates.

1. Read [package contract](references/fsm-package-contract.md) and [reviewed evidence](references/evidence.md). Capture project, target environment, intended create/update operation, exact business units, countries or OTHER, desired display switch, and six field behaviors. Do not select a live environment from this skill's evidence.
2. Read the six ora-resource files: [validation](ora-resource/ora_input_validation.md), [lookups](ora-resource/ora_reference_lookups.md), [dependencies](ora-resource/ora_dependency_readiness.md), [defaults](ora-resource/ora_defaulting_rules.md), [design gates](ora-resource/ora_design_enforcement.md), and [errors](ora-resource/ora_error_handling.md).
3. Route a fresh export and reference validation through the dependencies above. Resolve missing or ambiguous target identities. Compare requested changes with current data; preserve unrelated setup options and country rows. An absent ENABLE_TAX row is a supported create case, not an unsupported update. If the workbook explicitly says Update, resolve that lifecycle mismatch once; a user correction or explicit authorization to derive lifecycle from the baseline must be reused. Missing BU lookup evidence or an OAuth callback-port conflict is a separate prerequisite blocker, not evidence that creates are unsupported. Do not reuse another BU's candidate or approval even if all requested field values match.
4. Plan the existing compiled task rules using the [Expenses task rule execution guide](../references/task-rule-execution.md) and its local planner; require planned, ready status without an override. Reachable TBD contracts block runtime readiness. Source-backed UI defaults are not CSV import defaults.
5. The active runbook owns payload preparation; core.data-loader owns FSM preview, candidate-specific approval, submission, monitoring and reconciliation. Do not call Fusion REST, a browser writer, SQL, or an import utility directly from this task skill. No approval to author this skill authorizes a Fusion mutation.
6. After an authorized import, verify a fresh task export by business-unit/territory and ENABLE_TAX identities, report partial failures, and register sanitized results and token usage in the selected project. Do not retry failed or timed-out jobs automatically.

## Readiness limitations

BU and territory REST preflight contracts were exercised in the dated test campaign. Resolve them again in each target environment; prior tests do not establish current access or reference validity. Behavior membership is validated by the FSM entity, without requiring a separate public REST equivalent. Candidate audit cells follow the builder's empty-cell convention; all create business fields must be explicit, and update omissions preserve fresh baseline values. Both EXM_SETUP_OPTION.csv and EXM_CASH_ADV_SETUP_AND_POLICY.csv must contain identical minimal requested ENABLE_TAX rows under a maintained create/update profile or explicit nonproduction qualification. Other routine switch writes remain blocked; both aliases stay header-only for rule-only changes. An already-satisfied Update is reported and omitted from the delta, not used as a qualification test. EXM_VAT_FIELD.csv carries requested tax rules. Compiled rule readiness establishes authoring completeness, not target access or successful import. Fresh-export reconciliation is required after execution. The local alias helper performs no network operations and is not a complete task adapter or full live E2E certification.


## Repository-only unit tests

Run the [package CLI checks and transformation suites](tests/coverage.md) when
changing either Tax Fields helper. Package-local checks exercise the real CLI
boundaries; they supplement the broader synthetic migration tests below.

Developer tests and synthetic fixtures live under [Expenses test files](../noship/manage-tax-fields/TESTING.md).
Read that guide for the standard-library unittest command and the mapping to
campaign case IDs. These tests cover a local reference harness and mocked core
helpers; they do not certify Fusion setup or authorize execution. Exclude
`expenses/noship/` from deployed skill bundles. It is not part of the runtime workflow.


Automated test cleanup requirements are documented in
[cleanup test guide](../noship/manage-tax-fields/TESTING.md#cleanup-for-automated-test-runs).
Future live test runners must preflight a supported cleanup path, restore
changed setup and verify teardown even after test failures. Unsupported deletion
must block automated create fixtures unless the user explicitly requests
retention for that run. This developer-only policy adds no runtime delete route.
