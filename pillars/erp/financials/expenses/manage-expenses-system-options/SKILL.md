---
skill_id: "erp.financials.expenses.manage-expenses-system-options"
name: "Manage Expenses System Options Setup Task Guidance"
description: "Guides Manage Expenses System Options setup, including workbook intake, confirmed FSM option create/update package preparation, and FSM export-backed validation."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
task_code: "EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS"
task_name: "Manage Expenses System Options"
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
version: "0.7.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "expenses_system_options_input_workbook (optional)"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "expenses_system_options_intake_validation (when workbook supplied)"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-expenses-system-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-expenses-system-options/current/"
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
  - "Writes a local review-only FSM ZIP for confirmed option and scalar-setting creates and updates."
  - "Reads destination business-unit references through the shared REST client."
required_privileges:
  - "Read access to Financials business-unit LOV and task setup export."
---

# Manage Expenses System Options Setup Task Guidance

## Purpose

For fixed option dropdowns use the complete source-backed mappings in
[dropdown-value-contract.md](references/dropdown-value-contract.md). A selected
code need not occur in the target export. Do not use observed setup values to
infer the dropdown's domain.

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Expenses System Options` under `Expenses`.

## Setup Task Skill Contract

- task_code: `EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS`
- task_name: `Manage Expenses System Options`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Expenses System Options` under `Expenses`.

## Setup Task Metadata

- Task name: `Manage Expenses System Options`
- Task code: `EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS`
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
4. Prepare a package only with the confirmed create/update contract below, then import
   the immutable package with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Expenses`
- Setup task name: `Manage Expenses System Options`
- Setup task code: `EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS`

## Source-Backed Task Behavior

- Validate specific BUs through finBusinessUnitsLOV, independently of whether
  Expenses setup rows exist in the export. All Business Units uses the global
  identity with blank BuName and OtherOrgId=-1 for new option rows.
- Create or update confirmed option and scalar settings by their exact
  BU/code identity. Both paired option rows absent permits sparse insertion;
  one-sided absence, divergence and duplicate identities block preparation.
- Blank workbook values retain existing values or leave new overrides unset.
  Do not copy global IDs/audits or materialize unspecified inherited settings.
  Preserve unrelated rows and route imports through core Data Loader.
- Follow references/create-update-contract.md for source evidence, mapping
  limits, captured BU evidence and the separately governed live-import gate.

## Input Workbook

The [blank intake workbook](assets/ManageExpensesSystemOptions_Input.xlsx) uses the
same title, instructions, gray headers, banded tables, and 500-row capacity as
the Expense Report Templates input workbook. Its `User Options`, `Corporate
Options`, and `Processing Options` sheets reflect the supplied Fusion UI; each
has one row per business unit and one column per visible setting. `Field Guide`
lists each field's scope, input type, observed choices, CSV file, field code,
and mapping status. [The field catalog](references/intake-fields.json) is the
maintained source for workbook headers, validation lists, and code mappings.

For each section, use `All Business Units` in column A for enterprise-wide
settings, or the exact Fusion business unit name for a specific-unit override.
The workbook has no user-selected operation column. Resolve **Create** or
**Edit** from a fresh target setup-data export: if that business unit already
has a setup row in `EXM_SETUP_OPTION.csv`, `EXM_ORG_SETTING.csv`, or
`EXM_CASH_ADV_SETUP_AND_POLICY.csv`, every row for it is **Edit**; otherwise it
is **Create**. For Edit, every blank field is
unchanged and every filled field expresses a value change, even when the value
equals the current export. For Create, filled fields are the requested setup
values and blank fields are unset. Never fill blank Edit cells from another
workbook version or treat an identity-only row as a change. On a specific
business unit, `Use setup from all business units` requests inheritance;
`Employee Liability Account` also accepts `Use setup from Oracle Fusion
Payables`. The validator flags inheritance for a CSV representation check.
Specific BUs are validated through a fresh complete finBusinessUnitsLOV result,
not their presence in the export. Pass `--reference-evidence` to validate and
build-import; see references/create-update-contract.md.
For an existing business-unit override, removing its row from the import ZIP
does not establish inheritance: [Oracle's CSV setup comparison guidance](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/compare-task-setup-data.html)
states that CSV import does not delete target records. Keep inheritance blocked
until a task-specific, supported override-removal operation is established.
In the FSM CSV baseline, an empty `BuName` denotes the `All Business Units`
setup; resolve that workbook row to the same identity.
The UI's blank Printable Expense Report Format selection is intentionally not
represented as a clear operation because the export does not establish its
import semantics.

From this skill directory, run the bundled intake script using the Node runtime
returned by `load_workspace_dependencies`. The archive check also uses Python;
set `PYTHON` to that tool's bundled Python path if `python3` is not on `PATH`:

```text
node scripts/expense_system_options_intake.mjs create --output /absolute/path/ManageExpensesSystemOptions_Input.xlsx
node scripts/expense_system_options_intake.mjs validate --input /absolute/path/filled.xlsx --baseline-dir /absolute/path/extracted-current-data-export --baseline-process-id PROCESS_ID --baseline-archive /absolute/path/unchanged-export.zip --environment TARGET_ENV --reference-evidence /absolute/path/business-unit-reference-evidence.json --output /absolute/path/intake-validation.json
```

For specific Business Units, pass `--reference-evidence` to both `validate`
and `build-import`. Capture it through the declared shared REST client using
the [create/update contract](references/create-update-contract.md). Its target
environment and baseline ProcessId must match the selected export. A request
containing only All Business Units does not require this BU LOV evidence.

If the export metadata contains the observed FSM placeholder
`<ProcessId>-999</ProcessId>`, pass `--baseline-archive` with the unchanged
ZIP downloaded by `shared.setup-export.task-level-export`. The validator checks
its exporter-assigned filename, exact four member bytes, task, environment, and
completed-export metadata. The `--baseline-process-id` value is the real ID
returned by the export process, not `-999`. Do not alter the XML to make the
IDs match. The builder requires the same ZIP and checks its digest again.

The validator checks sheet headers, duplicate business units, formulas,
dropdown choices, yes/no values, nonnegative days, email and URL syntax. The
current-data export binds the operation to the target environment and its
ProcessId. The validator records a SHA-256 for each baseline CSV and emits
`operation: "edit"` or `operation: "create"` for each populated business-unit
row. Without `--baseline-dir`, local cell validation still runs, but the
operation is `unresolved` and a pending baseline check is reported. A
schema-only template export cannot resolve operations. The validator
normalizes filled fields to JSON with `issues` and `pending_checks`; blank
fields are omitted. It does not generate an import ZIP or mark a workbook
import-ready when an input is dynamic, unmapped, or inherited.
For a fresh baseline and confirmed option or scalar-setting **Create/Edit**
changes, it emits `ready_for_import: true`. Preserve filled
workbooks and normalized results only in the authorized project workspace;
they may contain customer setup data.

## Confirmed FSM Option Create/Update Package Contract

The task has a safe, narrow package-preparation path for a confirmed option
edit. It does not turn every workbook field into an importable value.

Use it only when the validation report has `ready_for_import: true`. That
requires all of the following:

- a completed, fresh data export from the exact target environment and task;
- no validation issues or pending mapping checks;
- one or more resolved **Create** or **Edit** operations; and
- changes mapped to `EXM_SETUP_OPTION` with an exact option/value code, or
  confirmed scalar `EXM_ORG_SETTING` text, email and nonnegative-integer fields.
  Dynamic references, candidate or unmapped fields, and both
  inheritance choices remain unsupported for package generation.

Build the package from the same extracted data export and validation result:

```text
node scripts/expense_system_options_intake.mjs build-import \
  --validation /absolute/path/intake-validation.json \
  --baseline-dir /absolute/path/extracted-current-data-export \
  --baseline-process-id PROCESS_ID \
  --baseline-archive /absolute/path/unchanged-export.zip \
  --environment TARGET_ENV \
  --reference-evidence /absolute/path/business-unit-reference-evidence.json \
  --output /absolute/path/ManageExpensesSystemOptions_Edit.zip \
  --manifest-output /absolute/path/import-manifest.json
```

The builder binds the supplied ProcessId to the export metadata or, for the
observed `-999` placeholder, to the unchanged exporter ZIP. It verifies
the validated workbook digest and every baseline CSV digest, preserves all
four exported members, and changes the uniquely matched or newly inserted
`(BuName, OptionCode)` rows in both `EXM_SETUP_OPTION.csv` and its paired
`EXM_CASH_ADV_SETUP_AND_POLICY.csv`. It submits only the complete selected rows,
retaining their existing non-value columns; unrelated rows are omitted from the
submission and must remain unchanged in Fusion. Other members remain header-only.
For a missing option in both paired files,
it appends a sparse row with BuName, OptionCode and ValueCode; global rows use
blank BuName and OtherOrgId=-1. It never copies global IDs or audits into a BU.
Confirmed scalar settings use BuName, SettingCode and SettingValue in
EXM_ORG_SETTING. No baseline usage is required for a new override.
It rejects duplicate or divergent paired rows, a changed baseline, a changed workbook, an invalid metadata identity, or
any unsupported field. The generated ZIP is a candidate artifact only: pass it
unchanged to `core.data-loader`, which performs its own preflight, Task Hook
validation, immutable approval, submission, monitoring, and ProcessLog
verification. Never submit the package directly.

### Selected-row submission and preservation evidence

`build-import` now uses the selected-row contract above. A prior full-baseline
regression changed last-update audits on an unrelated DFLT_CC_EXP_TEMPLATE_ID
row, despite identical submitted cells. That historical failure is retained;
full-baseline replay is no longer an ordinary builder behavior.

A controlled nonproduction create and update verified the selected-row profile:
48/48 create checks and 57/57 update checks passed, including preservation of
all 978 unrelated transport rows and their audit cells. See the bounded
[preservation evidence](references/selected-row-preservation.md). These cases
cover a BU-specific confirmed option and scalar setting, not every input,
global setting, target or release. Each run still needs fresh references,
native preflight/Task Hook approval and full post-import reconciliation.

For explicit developer qualification of a changed contract or scope, use the
[maintainer workflow](references/selected-row-qualification.md). Its separate
`build-qualification` command keeps the qualification-only warning and does not
grant ordinary promotion. Never remove an alias, rewrite metadata, replay an
uncertain import or repair audit fields to conceal a mismatch. No automatic
restoration, deletion or cleanup is implied.

## Export Evidence and Mapping Limits

The reviewed task-level CSV template and data exports for
`EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS` contain `EXM_SETUP_OPTION.csv`,
`EXM_ORG_SETTING.csv`, `EXM_CASH_ADV_SETUP_AND_POLICY.csv`, and
`ASM_SETUP_CSV_METADATA.xml`. The two option CSVs were identical in the
reviewed export; do not create duplicate intake columns from them. The template provides CSV
columns, not a complete value-code dictionary. The supplied UI screenshots
establish the six dropdown display lists captured in the field catalog.

Use the complete source-defined lookup mappings for the five fixed option
dropdowns in references/dropdown-value-contract.md. Export usage does not
limit valid choices. An observed code without a confirmed label match is not
enough to prepare an import. `candidate` and
`unmapped` fields, dynamic references (currencies, accounts, policies,
documents, pay groups, report templates), and enum choices with null codes
require source or UI verification. Report those checks to the user and retain
the original label in the intake result. Keep the existing source-backed rule
readiness gate below and route any future import through
`shared.validation.setup-data-validator`,
`shared.validation.reference-data-validator`, and `core.data-loader` with their
declared prerequisites and approvals.




## Source-Backed Rule Readiness

For configuration validation or change preparation, read
[reference lookups](ora-resource/ora_reference_lookups.md),
[dependency readiness](ora-resource/ora_dependency_readiness.md),
[design enforcement](ora-resource/ora_design_enforcement.md), and
[error handling](ora-resource/ora_error_handling.md). These resources cite the
Oracle customer documentation used for their functional rules.

The [compiled rule registry](ora-resource/ora_rule_registry.json) covers the
confirmed FSM option create/update contract above. Run the resource-authoring planner
for this task and require a current ready plan before consuming those nodes.
The plan confirms the validated intake evidence, fresh baseline binding,
package-preservation conditions, and the mandatory `core.data-loader` handoff;
it does not grant approval or claim that an import completed. Baseline exports
use the separately declared CSV export workflow and its own preflight
requirements.

For a requested field outside the confirmed create/update contract, classify the
request as `unsupported_by_confirmed_fsm_contract` and report the exact field
and missing source or mapping evidence. Do not use a registry-readiness
override to prepare or submit an import.

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
