# Manage Expenses System Options Input Validation

The executable validation boundary is deliberately limited to confirmed FSM
option edits. It validates a locally produced intake-validation result and the
fresh export it binds; it does not infer mappings for dynamic references,
or inheritance. Creates and missing overrides use sparse rows with exact destination BU validation.

## Sources

- [Oracle Fusion Cloud Applications: Using Functional Setup Manager, 26D](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/using-functional-setup-manager.pdf)
- [Oracle 26D: Compare Task Setup Data](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/compare-task-setup-data.html) (CSV import does not delete existing target records)
- Task-local `scripts/expense_system_options_intake.mjs` validation and package builder

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Validated intake evidence | intake-validation.json with task_code EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS, source workbook SHA-256, baseline environment, ProcessId, CSV SHA-256 values, ready_for_import true, records, no issues, and no pending_checks | Block package preparation | Revalidate the unchanged workbook against a fresh completed target data export | Every confirmed FSM option create/update package | |
| Supported requested edits | One or more Create/Edit records with exact confirmed OptionCode/ValueCode or supported scalar SettingCode/SettingValue | Block package preparation | Remove or separately source dynamic, unmapped or inherited changes | Every confirmed FSM option create/update package | |
| Fresh baseline package | ASM_SETUP_CSV_METADATA.xml plus EXM_SETUP_OPTION.csv, EXM_ORG_SETTING.csv, and EXM_CASH_ADV_SETUP_AND_POLICY.csv from the validation result's completed export | Block package preparation | Export the exact task again from the intended target and revalidate | Every confirmed FSM option create/update package | |

## Field Validation

Fixed dropdown label/code pairs come from
[dropdown-value-contract.md](../references/dropdown-value-contract.md) and the
catalog's lookup_type, never from baseline usage. All five fixed lists have
complete code mappings. Dynamic report-template references remain separate.

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Task and environment binding | Require the validation task code, metadata ObjectShortName, ProcessType, ProcessStatus, ProcessEnv, and CSV digests to agree with the supplied baseline. Match the metadata ProcessId to the export job ID, or accept the observed `-999` placeholder only when the unchanged exporter ZIP has the expected environment/task/job filename and all four members match the extracted files byte for byte | Every confirmed FSM option create/update package | |
| Workbook immutability | Require the workbook's current SHA-256 to equal the digest in intake-validation.json | Every confirmed FSM option create/update package | |
| Exact option identity | Require at most one row per BuName/OptionCode in each paired file; both absent permits sparse insertion, both present permits a ValueCode update, and divergent presence or values blocks. New global rows use OtherOrgId=-1. Scalar settings upsert by BuName/SettingCode | Every confirmed FSM option create/update package | |
| Package member preservation | Retain four members, exact fresh descriptor bytes and ordered headers. Emit only complete selected rows, preserve their non-input cells and both aliases, and leave unselected entities header-only. Omit unrelated baseline rows; verify their full persisted values and audits after import. Candidate conformance is not live success | Every confirmed FSM option create/update package, ordinary or explicit nonproduction qualification | |
| Qualification boundary | Require the user-selected nonproduction environment, qualification-only manifest, exact selected-key intent, submitted/omitted row counts and pending-preservation warning. No ordinary customer promotion, alias removal, metadata rewriting or silent rule override | A build-qualification candidate is requested | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMSO.VALIDATE_EDIT_INPUT | step | 1 | validate_input | valid->EXMSO.CONFIRM_BASELINE;invalid->EXMSO.RETURN_ISSUES | none | stop | A confirmed FSM option create/update package is requested |
