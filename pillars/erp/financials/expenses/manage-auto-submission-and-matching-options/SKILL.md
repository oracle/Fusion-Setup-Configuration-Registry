---
skill_id: "erp.financials.expenses.manage-auto-submission-and-matching-options"
name: "Manage Auto Submission and Matching Options Setup Task Guidance"
description: "Configure reviewed Expenses auto-submission schedules and matching options from customer business input on a selected Fusion environment, with target validation, change-only FSM composition and governed approval."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
task_code: "ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS"
task_name: "Manage Auto Submission and Matching Options"
parent_skill_id: "erp.financials.expenses"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "ERP financials pillar team"
version: "0.4.4"
inputs:
  - "fusion_environment_context"
  - "input_workbook_or_business_values"
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "fsm_candidate_archive (when changes require import)"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "erp.financials.organization-structures"
  - "core.runbook"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-auto-submission-and-matching-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-auto-submission-and-matching-options/current/"
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
    - "Oracle Fusion releases whose fresh task export matches the supported FSM schema contract; no release-number allowlist"
side_effects:
  - "Writes a local candidate ZIP to a new explicitly selected protected path before core validation and approval."
  - "Delegates approved template/baseline export jobs to shared.setup-export.task-level-export."
  - "Delegates read-only identity checks to the shared Fusion REST client."
  - "Delegates qualified, preview-approved FSM imports to core.data-loader."
required_privileges:
  - "Task-specific Fusion setup export/import privileges in the selected environment."
  - "Visibility to verify the requested business-unit identity and applicable setup reference values."
---

# Manage Auto Submission and Matching Options Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Auto Submission and Matching Options` under `Expenses`.

## Setup Task Skill Contract

- task_code: `ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS`
- task_name: `Manage Auto Submission and Matching Options`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Auto Submission and Matching Options` under `Expenses`.

## Setup Task Metadata

- Task name: `Manage Auto Submission and Matching Options`
- Task code: `ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Review ownership

Owner: ERP Financials pillar team. Required reviewers: Expenses pillar SME and FSCR core reviewer.

Developer-only automated unit tests and the run command are documented in
[Expenses noship tests](../noship/manage-auto-submission-and-matching-options/TESTING.md).
These offline tests are not a runtime dependency. The task-local
[noship discovery entry point](noship/tests/test_noship_suite.py) runs that same
suite for package-local validation. Release tooling must exclude both
`expenses/noship/` and this task's `noship/` from deployed skill bundles.

## Business-unit selection and prerequisite routing

A supplied Business Unit, BU Name, or BuName selects **BU-scoped modification of this task's expense settings**. Do not ask the user to choose create versus update again when that intent is unambiguous. This does not request a change to the business-unit master. Use the user's latest explicit target environment over stale workbook environment values; conflicting explicit scope or BU values require clarification. A blank BU never implies global scope.

The active Run Book owns the following cross-task orchestration. Task resources return dependency outcomes; they do not create business units or sequence another task inside this task's registry.

1. Discover the exact setup task in the effective repository catalog and its generated task files. For this setup use ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS. For a missing BU use **FUN_MANAGE_BUSINESS_UNIT**, **Manage Business Unit**, under Financials / Organization Structures. Accept either a flat metadata file or a nested skill; require a unique catalog/owner match. The current BU route is [Manage Business Unit](../../organization-structures/manage-business-unit.md), owned by [Organization Structures](../../organization-structures/SKILL.md). Load that owner and its task resources rather than generating a duplicate BU skill.
2. Through the selected workflow, verify BU existence using the task's reference-lookup contract. A unique usable BU permits the requested expense modification only after the remaining task gates pass. Preserve unspecified settings. An absent expense-option or organization-setting row is not proof that the BU is absent and does not authorize BU creation or a guessed setup-row insertion.
3. Only a confirmed absent BU triggers this prompt: **“Business unit '<name>' does not exist in '<environment>'. To create it, provide its Default Reference Set (existing Set Code, or a new Set Code and Set Name), operational purpose and accountable owner. You can also correct the business-unit name.”** Reuse already supplied details. Collect the owning BU skill's additional applicable design inputs, including business functions and financial foundation when required; location, manager and Active choice remain optional unless that task's applicable contract requires them. Do not request generated Oracle IDs.
4. When the user supplies creation details, invoke the discovered Manage Business Unit workflow through the Run Book, with create intent and the same target environment. Use its default-set resolution, duplicate check against fresh target export, validation and Data Loader approval gates. Related set or function setup must use the owning repository skills. Do not substitute direct REST writes or browser entry when a route is incomplete.
5. After creation is confirmed through the owning workflow, reverify the BU and resume the original expense modification with fresh validation and preview. Accepted job initiation alone is not proof that the BU exists. If confirmation requires a later status request, leave this task waiting for that confirmation.

Multiple matches, an inactive BU, incomplete pagination, insufficient visibility, authentication failure or an unavailable lookup mean **unverified or unusable**, not nonexistent. Explain the actual result and request the corresponding correction; never turn these outcomes into a create request. If the BU skill is missing, ambiguous or not executable, report its exact task code and missing contract and stop that prerequisite. The dependency remains visible until resolved.

This is the user-requested routing policy, not new evidence of Oracle import behavior. Existing task readiness stops still apply, including to live lookups; discovering the BU skill does not itself authorize execution.

## Execution workflow and scope

Read [customer input and environment changes](references/customer-input.md) for
conversation, tables, XLSX, CSV/TSV, JSON, YAML, text/Markdown and assisted
document/image intake. Use its environment-binding check on every new target.
The host reads the supplied input and retains explicit business values in memory;
the task adapter prepares an FSM candidate for core Data Loader. Unknown
inputs are reported, never silently discarded.


Read [the portable execution contract](references/execution-contract.md) for
fresh-clone setup, user-input normalization, environment selection, compatibility
checks and the exact maintenance Data Loader handoff. It replaces dependencies on
private project artifacts or this skill's authoring conversation. Use Python
3.10 or newer for the repository's existing scripts.

The canonical entry point for an implementation request is
[Implementation Router](../../../../../router/implementation-router/SKILL.md).
Select a project and activate its Run Book through the owning core workflow.
Keep credentials in core-managed local configuration/cache, never this skill.
Use user-supplied environment and inputs; no pod, BU, scope, client or Run Book
ID is a built-in default.

This skill maps reviewed auto-submission and receipt/card matching controls to
source-backed setting codes. Auto-submission permits explicit global or BU
scope. Matching changes require explicit global scope; a BU-specific request
must be clarified, not broadened silently. Omitted controls preserve existing
settings. Cash-advance policy editing and unrelated feature provisioning remain
outside this task's implemented input contract.

Read the resources in this order:

1. [Input validation](ora-resource/ora_input_validation.md).
2. [Dependency readiness](ora-resource/ora_dependency_readiness.md).
3. [Reference lookups](ora-resource/ora_reference_lookups.md).
4. [Defaulting](ora-resource/ora_defaulting_rules.md).
5. [Design enforcement](ora-resource/ora_design_enforcement.md).
6. [Error handling](ora-resource/ora_error_handling.md).

Load the [compiled registry](ora-resource/ora_rule_registry.json) and the
[Task Node Execution Guide](../references/task-rule-execution.md).
Require a planned ready graph without a readiness override. Then evaluate the
actual runtime dependencies. **Ready describes authored rules, not target
qualification or permission to import.** The shared-alias selection check (when setup-option rows actually change) and
blank/global serialization are explicit product-qualification checks; they are not solved
by compiling the registry. The portable contract states the required evidence. The shipped
[organization-setting transport profile](references/fsm-transport-profile.md)
supplies the source-backed contract and verified successful organization-setting
import for its exact schema. This does not qualify populated option aliases. Customers supply environment and business
input; the workflow obtains its own template/baseline. A prior import ZIP is
not a customer prerequisite. Customers do not supply the technical CSV members
or select a winning alias. Follow the [customer-side package and alias policy](references/customer-input.md#repository-only-customer-workflow)
to obtain the files, reconcile current values and distinguish supported changes
from an unresolved product contract. A missing package is an export-workflow
dependency, not a request for the customer to build an import ZIP.
Do not silently remove, waive or assume those checks.

Maintainers implementing the option-alias limitation may use the separately
declared [controlled qualification workflow](references/option-alias-qualification.md)
only after the user selects a non-production target and test/restoration change.
This branch preserves core's preview approval and every other task gate; it
does not qualify the candidate for ordinary customer runs by itself.

Use [input_contract.py](scripts/input_contract.py) to check normalized user
intent offline. A passed input check is not a package or an approval. Use the
task's [candidate preparation helper](scripts/fsm_session.py) with a fresh same-task template,
normalized user values and a new absolute `--output` ZIP path in authorized
protected local storage. The historical filename is retained; it uses no
interactive core session API. Keep
every CSV member and original metadata; empty
unrequested files retain their headers. `businessObject` remains empty; archive
identity comes from ASM_SETUP_CSV_METADATA.xml ObjectShortName.

Only after the environment, schema, alias, serialization, scope and value checks
pass, prepare the candidate, run core preflight, evaluate the exact immutable
artifact through Task Hook and retain its preview. Present core's approval
report only after all task rules pass. Approval binds the retained artifact,
target and active Run Book. Use core's retained preflight and unchanged Task
Hook approval envelope for submission; never treat candidate preparation as
approval. The portable contract gives the exact commands. Report
accepted initiation immediately; status/reconciliation uses the core workflow
on a subsequent user request. No direct REST or browser write fallback.
Redact credentials, secrets and customer values from durable diagnostics.
Keep candidates and core-required internal approval records in authorized
protected local storage under core's retention policy, never tracked source.

Always confirm the user's time zone for the run. If workbook, session or target
values conflict, ask the user to choose and confirm; never substitute silently.
Reuse a later explicit confirmation. See the portable contract for the lookup.

For any BU schedule request, apply the [BU schedule display check](references/execution-contract.md#verify-the-bu-schedule-display-before-approval), including inherited and already-satisfied cases. Enablement is explicit user input, never a default. Resolve visibility intent before Task Hook approval.

For enabling auto submission, resolve the resulting complete schedule from
explicit changes plus verified current values: at least one weekday, valid
HH:mm and a verified time-zone code. Do not default missing schedule values or
require the user to repeat values already established by an approved baseline.
Setup UI initialization can insert defaults; do not open it as a read-only check.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-evidence-unresolved-operations:  -->

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Expenses`
- Setup task name: `Manage Auto Submission and Matching Options`
- Setup task code: `ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS`




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

Supported create/update operations are bounded to organization-setting rows
under the shipped transport profile. A required setup-option write remains
blocked by FSM_ALIAS_COLLISION; these markers do not waive that check.
