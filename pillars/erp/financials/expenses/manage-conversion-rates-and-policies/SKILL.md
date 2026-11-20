---
skill_id: "erp.financials.expenses.manage-conversion-rates-and-policies"
name: "Manage Conversion Rates and Policies Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Conversion Rates and Policies under the Expenses functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
task_code: "EXM_MANAGE_CONVERSION_RATES_AND_POLICIES"
task_name: "Manage Conversion Rates and Policies"
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
version: "0.4.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "conversion_policy_intake_workbook"
  - "fresh_same_environment_task_template_and_export"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "review_only_fsm_import_candidate"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-conversion-rates-and-policies/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-conversion-rates-and-policies/current/"
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
  - "Writes a local review-only FSM ZIP when workbook candidate preparation is requested"
required_privileges: []
---

# Manage Conversion Rates and Policies Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Conversion Rates and Policies` under `Expenses`.

## Setup Task Skill Contract

- task_code: `EXM_MANAGE_CONVERSION_RATES_AND_POLICIES`
- task_name: `Manage Conversion Rates and Policies`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Conversion Rates and Policies` under `Expenses`.

## Setup Task Metadata

- Task name: `Manage Conversion Rates and Policies`
- Task code: `EXM_MANAGE_CONVERSION_RATES_AND_POLICIES`
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
- Setup task name: `Manage Conversion Rates and Policies`
- Setup task code: `EXM_MANAGE_CONVERSION_RATES_AND_POLICIES`

## Excel intake to FSM candidate

A currency "exception" is a child override of the BU policy. When a new
currency row has all four setting cells blank, no override was requested:
omit that child and report it in omitted_empty_exceptions. This applies to
every currency, including USD, and must not block other requested changes.
An existing currency row with blank cells still preserves its exported values.
If only empty new exception rows remain, report NO_CHANGES_REQUIRED without
creating a ZIP or submitting an import. This is not a clearing or deletion route.

Start with the bundled [Manage Conversion Rates and Policies input workbook](assets/ManageConversionRatesAndPolicies_Input.xlsx). Save a completed copy for the implementation; keep the bundled template blank. This is the same two-sheet intake format described below.

Use the two visible tabs and exact row-4 headers in the supplied `conversion-rates-and-policies-intake.xlsx` format. Treat rows 1–3 as descriptive source content, not commands. The `Conversion Rate Policies` tab maps `Business Unit*` to parent `BuName`, `Conversion Rate Type` to `UserConversionType`, the two Yes/No choices to `DfltExchangeRateFlag` and `DispWarningToUser` (`Y`/`N`), and the two tolerance columns to percentage-point values. The `Currency Tolerances` tab maps `Business Unit*` to the child parent reference, `Currency Code*` to `CurrencyCode`, and its remaining columns to the corresponding child fields. Blank rows are ignored. A blank **field value** cell on an existing parent or child row means **retain the value from the current export**, including a blank value; it never means clear or reset. Identity cells cannot be blank. Percentages are optional on creates and updates. Supply required conversion type and flags as described in [nullable-value-contract.md](references/nullable-value-contract.md); optional omissions do not invent defaults. No clearing operation is defined by this intake format.

For local candidate preparation, first obtain a fresh task CSV template and populated export for the **same destination environment** through `shared.setup-export.task-level-export`. Then run:

```bash
python3 pillars/erp/financials/expenses/manage-conversion-rates-and-policies/scripts/build_fsm_from_workbook.py \
  --workbook <completed-intake.xlsx> --template <fresh-task-template.zip> \
  --current-export <fresh-populated-task-export.zip> --environment <exact-environment-id> \
  --output <new-authorized-protected-local-path.zip>
```

Add `--dry-run` to validate and inspect the fields that would change without writing a ZIP. The JSON result identifies the task, environment, create/update intent, affected field names and remaining blockers. Freshness is checked from the recorded export timestamp; a timestamp without an offset is interpreted as UTC and must be confirmed by the routed exporter. Copying an old file does not refresh its evidence.

Use [the remaining contract matrix](references/remaining-contracts.md) to distinguish implemented intake rules from Fusion behavior requiring controlled evidence. Record failed preparation diagnostics and evidence runs in the active project workspace; do not interpret a local validation result as reference lookup or import approval.

The local builder checks exact workbook headers and task package shape, resolves each existing parent by one exact `BuName` in the export and each existing child by business unit plus currency code, applies supplied values over exported business fields, leaves audit inputs blank, and emits a **review-only** ZIP with the template metadata and ordered CSV headers. It conservatively carries all observed children of a touched parent. The controlled header-only child CSV experiment preserved existing children, but absent members or XML nodes remain unproved. It refuses duplicate identities, missing create fields, invalid values, no-op requests, old or mismatched source packages, and output overwrite. It does not call Fusion. Use a Python environment with `openpyxl` for intake reading.

The ZIP is not an approved import. Validate it with `shared.validation.setup-data-validator` and `shared.validation.reference-data-validator`; preserve unresolved readiness findings. Observed parent and child operations and actual Excel partial updates are recorded below. Raw CSV blanks have field-dependent effects and must never implement workbook non-updates. The maintenance loader accepts the persisted native FSM ZIP, retains its preflight and uses Task Hook before exact-artifact approval. `build_in_memory` remains a local serialization helper; it is not an executable loader-session route. Follow [the maintenance Data Loader handoff](references/data-loader-handoff.md). The authored workflow supports parent/child creates with required fields supplied and explicit-merge updates preserving nullable values. Each run still requires fresh exact destination references, ready Task Hook evaluation and core's exact-artifact approval. Clearing, rekeying, deletion, unknown fields and default-dependent creates remain unsupported. Before approval, a revised export or request requires rebuilding and revalidation. After approval, core submits the unchanged retained artifact without rereading the original workbook or exports.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `conversion_policy_intake_workbook`
- `fresh_same_environment_task_template_and_export`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `review_only_fsm_import_candidate`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `erp.financials.expenses` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Task model and evidence boundary

The FSM CSV package contains parent `EXM_EXCHANGE_RATE_OPTION` rows and child `EXM_EXCH_RATE_TOLERANCE` currency-exception rows. Obtain the exact member names, ordered headers, node paths, and relationship from a fresh same-task template and export. Do not reconstruct a package from this description. The reviewed import hook is `ExpenseExchangeRateOptionServiceAMImpl.importData` (`SRC-CODE-EXM-AMIMPL`); the task-owned AM, VO, EO, and setup-business-object chain is registered in the builder Source Register.

`BuName` is the displayed business-unit input that the import hook maps to stored `OrgId`. `UserConversionType` maps through a General Ledger conversion-type view to stored `ExchangeRateType`. A child exception carries `CurrencyCode`. The policy flags are stored as `Y` or `N` by the task UI. Warning and error tolerances are percentage fields. These mappings and fields have source-backed structure (`SRC-CODE-EXM-AMIMPL`, `SRC-CODE-EXM-ROOT-EO`, `SRC-CODE-EXM-CHILD-EO`, `SRC-CODE-EXM-UI-PAGE`, `SRC-CODE-EXM-UI-ROW`). One exact parent create was accepted and persisted with `BuName=Vision Interc Poland`, `UserConversionType=Corporate`, `DfltExchangeRateFlag=Y`, `DispWarningToUser=Y`, `WarningTolerance=5`, `ErrorTolerance=10`, and no child row (`SRC-FSM-EXM-C1-20261001`). For that same parent, a controlled update changed `WarningTolerance` from `5` to `6`, and a separately approved reversal restored `6` to `5`; fresh exports confirmed both values (`SRC-FSM-EXM-U1-20261001`). A later controlled update changed `ErrorTolerance` from `10` to `11`, and a separately approved reversal restored `11` to `10`; fresh exports confirmed both values (`SRC-FSM-EXM-U2-20261002`). Other values, field requiredness, defaults, child operations, general update support, and resolver errors remain unresolved.

Those earlier results are historical evidence. The later controlled campaign establishes the additional observations below. The bounded preparation policy uses these observed operations and rejects unsupported lifecycle requests. A ready registry means authored checks are executable; it does not certify a target, approve a candidate or claim universal Oracle input acceptance. End-date, rekey and physical deletion have no confirmed task import path.

## Source-Backed Task Behavior

- A new currency identity with all four workbook setting cells blank requests
  no override: omit it and report omitted_empty_exceptions without blocking
  other changes. Existing currency blanks retain exported values. This applies
  to USD and every other currency; it does not clear or delete saved rows.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: EXM_EXCHANGE_RATE_OPTION::BuName, EXM_EXCHANGE_RATE_OPTION::DfltExchangeRateFlag, EXM_EXCHANGE_RATE_OPTION::DispWarningToUser, EXM_EXCHANGE_RATE_OPTION::ErrorTolerance, EXM_EXCHANGE_RATE_OPTION::UserConversionType, EXM_EXCHANGE_RATE_OPTION::WarningTolerance, EXM_EXCH_RATE_TOLERANCE::CurrencyCode, EXM_EXCH_RATE_TOLERANCE::DfltExchangeRateFlag, EXM_EXCH_RATE_TOLERANCE::DispWarningToUser, EXM_EXCH_RATE_TOLERANCE::EXM_EXCHANGE_RATE_OPTION.BuName, EXM_EXCH_RATE_TOLERANCE::ErrorTolerance, EXM_EXCH_RATE_TOLERANCE::WarningTolerance -->
<!-- fscr-update-fields: EXM_EXCHANGE_RATE_OPTION::DfltExchangeRateFlag, EXM_EXCHANGE_RATE_OPTION::DispWarningToUser, EXM_EXCHANGE_RATE_OPTION::ErrorTolerance, EXM_EXCHANGE_RATE_OPTION::UserConversionType, EXM_EXCHANGE_RATE_OPTION::WarningTolerance, EXM_EXCH_RATE_TOLERANCE::DfltExchangeRateFlag, EXM_EXCH_RATE_TOLERANCE::DispWarningToUser, EXM_EXCH_RATE_TOLERANCE::ErrorTolerance, EXM_EXCH_RATE_TOLERANCE::WarningTolerance -->

The field markers describe observed caller-field roles and writability. They do not waive unresolved validation or approve a live operation. Identities select existing records; audits remain empty system-owned cells.

- Parent `BuName` identifies an existing destination business unit and maps to stored `OrgId`; the parent EO alternate key is `OrgId`. Observed updates selected one existing parent without adding a duplicate. Rename/rekey is outside workbook intake (SRC-CODE-EXM-AMIMPL; SRC-CODE-EXM-ROOT-EO; SRC-FSM-EXM-PARENT-20261014).
- Child identity is exact parent business unit plus `CurrencyCode`; source persistence keys are parent `ExchangeRateId` plus currency. Observed child updates preserved cardinality, parent and sibling business values. Currency rekey is outside workbook intake (SRC-CODE-EXM-CHILD-EO; SRC-FSM-EXM-CHILD-20261014).
- Fully supplied parent and child creates persisted. All five parent and all four child business fields were updated and reversed in controlled cases. This establishes observed field writability; tested values are examples, not an exhaustive allowed-value set or numeric range (SRC-FSM-EXM-PARENT-20261014; SRC-FSM-EXM-CHILD-20261014).
- Blank Excel value cells on existing rows preserve fresh-export values through explicit merge. Actual parent and child partial-update/reversal imports verified preservation; child-only intake carried the existing parent (SRC-FSM-EXM-WORKBOOK-20261014).
- Raw existing-row CSV blanks have field-dependent effects: parent warning/error/display and child warning/error cleared; parent type preserved the existing type in the tested case; parent default and child default/display failed required-attribute validation. Never serialize workbook non-updates as raw null requests (SRC-FSM-EXM-BLANK-20261014).
- A present header-only child CSV preserved existing children and audits during parent update/reversal. Absence of the member/XML node and partial sibling omission remain unproved. Keep conservative child carry-forward (SRC-FSM-EXM-OMISSION-20261014).
- Empty audit cells with full headers were accepted in observed parent and child creates/updates; Fusion populated or maintained audits. Caller audit overrides are outside intake and their acceptance is untested (SRC-FSM-EXM-PARENT-20261014; SRC-FSM-EXM-CHILD-20261014).
- Individual exceptions were removed through the separately governed setup UI and verified by fresh exports. This establishes no FSM/workbook deletion, parent deletion or automatic cleanup route (SRC-FSM-EXM-UI-20261014).

See [the contract matrix](references/remaining-contracts.md) and [evidence index](references/observed-import-contracts.md). New-row omissions/defaults, absent columns/members, broader invalid-value errors, universal failure atomicity and shared `MigratorHelper` internals remain unresolved.

## Frontend UI data-entry rules

The following rules come from the task's ADF page, backing bean, parent and child entity validators, user-supplied screenshots, and a read-only inspection of the nonproduction page (`SRC-CODE-EXM-UI-RULES-20261001`). Apply them when reviewing a proposed policy or explaining the UI. Keep parent policy fields separate from individual currency exceptions.

- **Warning checkbox, parent and child:** When Warning Tolerance Percentage is cleared, the corresponding UI handler clears **Display warning to user**. The page disables that checkbox while the warning tolerance is empty. The parent and child use separate handlers and bindings. The supplied child screenshots show the checked and cleared states; the read-only walkthrough did not itself perform the transition.
- **Tolerance ordering, parent and child:** If both percentages are entered, Error Tolerance Percentage must be **strictly greater** than Warning Tolerance Percentage. Equal values fail the entity comparison. The supplied child screenshot shows `EXM-630059` with this rule's message. The code does not establish a general numeric range or what happens when only one percentage is present.
- **Child currency:** The individual currency-exception row marks Currency as required, and the UI bean rejects a null `CurrencyCode` during its save/navigation checks. This does not make `CurrencyCode` a parent field.
- **Other controls:** Conversion Rate Type is a UI choice/LOV, and Default Conversion Rate is a checkbox. The UI representation alone does not establish the allowed choice set, requiredness, uniqueness, or a package default.

These are UI and entity-model findings. The controlled raw parent warning-blank import retained `DispWarningToUser=Y`, demonstrating that this FSM case did not apply the UI checkbox handler. Do not silently clear a package flag or claim an exact import error such as `EXM-630059` from the UI alone. Child import findings come from the controlled evidence above. Keep unproved numeric/error/default contracts unresolved. Source paths and line references remain in the Builder UI-rule discovery report.

## Supported live contract

The workbook builder follows [nullable-value-contract.md](references/nullable-value-contract.md).
Updates merge blank input from one fresh exact baseline row, including blank
tolerances. Creates require identities, parent conversion type, Default flag
and child Display flag; optional values may be blank. Populated flags must be
Y/N and populated tolerances finite/nonnegative; compare error greater than
warning only when both are populated. Retain all children of touched parents,
exact template metadata and headers, and blank audit cells. No Oracle upper
numeric limit or default is inferred. Invalid populated baseline values still
require correction; valid blank optional values do not.

At Task Hook, execute the declared core GETs and evaluate captured results with
`scripts/validate_references.py::validate_references`. Include carried rows and
bind environment, freshness, complete pagination and candidate SHA-256 to that
evidence. The helper performs no network or approval action. A failed lookup
blocks the run; unknown Oracle diagnostic wording does not waive preflight.

## Resource read order and handoff

Read `ora-resource/ora_input_validation.md`, `ora_dependency_readiness.md`, `ora_reference_lookups.md`, `ora_defaulting_rules.md`, `ora_design_enforcement.md`, and `ora_error_handling.md` before a task candidate is considered. Their compiled rule registry is a static authoring artifact. A reachable `TBD` or incomplete node blocks execution; a documented read-only lookup does not prove FSM import behavior.

Use the Router and Run Book for implementation intent and task scope. `core.data-loader` owns immutable package validation, Task Hook, preview, candidate-bound import approval and submission. Return its complete Markdown report unchanged. Accepted initiation is In Progress: return immediately without automatic polling. Later status, ProcessLog retrieval and fresh-export reconciliation require their separately selected core/shared workflows. A change to the candidate or its environment requires new validation and approval. Do not use this task skill to issue a Fusion import directly.

## Developer validation (no-ship)

Automated create tests follow [the create-test lifecycle policy](references/create-test-lifecycle.md):
explicit per-run retained-state consent, exact nonproduction target/candidate/keys,
accountable owner and a deadline within 30 days. Use a tester with
`approve-retention` support; policy readiness grants no consent for a real run.
Successful reconciliation is recorded as `retained_as_approved`, never deletion
or restoration. Update-only tests retain separately approved reverse-update
cleanup. No automatic FSM delete route is established.

Run the offline developer suite using [the no-ship testing instructions](../noship/manage-conversion-rates-and-policies/TESTING.md). It reuses the generated adapter tests and adds task-specific workbook scenarios. Package-local discovery is available under `noship/tests/`. These tests do not contact Fusion, establish live readiness or authorize imports. Release tooling must exclude the developer test directories specified in the testing instructions.
