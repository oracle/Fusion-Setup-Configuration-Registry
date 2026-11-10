# Manage Expenses System Options Dependency Readiness

## Sources

- [Oracle Fusion Cloud Applications: Using Functional Setup Manager, 26D](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/using-functional-setup-manager.pdf)
- [Setup Task CSV Imports REST endpoints, 26D](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/api-setup-task-csv-imports.html)
- Task-local `scripts/expense_system_options_intake.mjs` validation and package builder

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Validated edit input | Confirm the requested changes are supported, mapped, and bound to the unchanged workbook |
| 2 | Fresh task baseline | Confirm the complete export identity, required members, exact rows, and CSV digests |
| 3 | Preserved package and handoff | Build the declared ordinary or explicit nonproduction qualification package, change only confirmed requested business fields, and hand the exact artifact to core.data-loader unchanged |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| EXMSO.INPUT | Confirmed option-edit input | Yes | Every confirmed FSM option create/update package | Verify | intake-validation.json created by the task-local validator | | The package builder can safely change only exact confirmed option codes and value codes | Revalidate after any workbook change | Task code, workbook digest, Edit records, OptionCode, ValueCode, issues, and pending checks |
| EXMSO.BASELINE | Fresh completed task export | Yes | Every confirmed FSM option create/update package | Verify | The exact four-member data export selected by the validation result | resolve_expenses_option_edit_baseline | A data export provides the task schema, target binding, and existing rows to preserve | Re-export and revalidate when any metadata or CSV digest changes | Environment, ProcessId, metadata identity, source CSV digests, normalized BuName, OptionCode, and matched rows |
| EXMSO.PACKAGE | Immutable package preservation | Yes | Before Data Loader preflight | Verify | Package-builder manifest and the generated ZIP | | The candidate must retain task identity and match its declared submission scope; selected-row qualification is not a live-preservation assertion | Pass the exact ZIP and manifest to core.data-loader; restart validation after any package change and retain the qualification warning | Four members, exact descriptor, ordered headers, package digest, selected keys, submission counts and conformance result |
| EXMSO.LOADER | Mandatory Data Loader handoff | Yes | Before any import submission | Verify | core.data-loader preflight and Task Hook evidence | | Data Loader owns validation, immutable approval, submission, monitoring, and ProcessLog retrieval | Do not call an FSM import endpoint or UI import directly | Data Loader preflight result, Task Hook result, approval binding, request identifier, and later verification result |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMSO.CONFIRM_BASELINE | step | 2 | resolve_dependency | satisfied->EXMSO.DATA_LOADER_HANDOFF;unresolved->EXMSO.RETURN_ISSUES | EXMSO.VALIDATE_EDIT_INPUT | stop | A confirmed FSM option create/update package passed input validation |
