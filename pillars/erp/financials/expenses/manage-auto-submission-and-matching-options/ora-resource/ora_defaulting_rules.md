# Defaulting rules

These rules are reusable across target environments. Planner readiness means the execution rules are defined; all applicable runtime checks must still pass. The portable execution contract in ../references/execution-contract.md defines environment selection, input mapping, FSM compatibility checks and the in-memory Data Loader handoff. A missing product qualification is an explicit runtime blocker, never implicit approval.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| EXM_ORG_SETTING.SettingValue | No skill-supplied business default. A provided value is validated per control; omitted update controls are unchanged; a requested new setting requires an explicit value | Candidate create or update | No | resolve_setting_value |
| EXM_SETUP_OPTION.ValueCode | No skill-supplied default. Require an explicit Yes/Y or No/N when changing or inserting the enable control; omitted update controls are unchanged | Candidate create or update | No | resolve_auto_submission_value |
| EXM_SETUP_OPTION.OtherOrgId | -1 for explicit global scope; empty field for a named verified BU. These source-backed scope representations require qualify_fsm_transport before submission | Global setup-option request after scope is confirmed | No |  |
| Audit fields | Empty CSV fields with headers retained; never copy historical users/dates or accept audit edits. qualify_fsm_transport must confirm applicable blank serialization | Candidate serialization | No |  |

## Source distinctions

| Evidence | Boundary |
|---|---|
| UI direction defaults POSITIVE, NEGATIVE and BOTH | UI initialization is not an FSM import default contract. |
| Blank BuName in organization-setting import maps to -1 | Do not infer that omitted scope means global. The shipped organization-setting transport profile covers its exact schema; other representations need qualification. |
| Setup-option global branch compares OtherOrgId text with -1 | Do not copy numeric BU IDs across environments or collapse this branch into the organization-setting rule. |
| Runtime global fallback when BU option row is absent | An existing row with a non-enabling value is not the same as an absent row. Runtime fallback does not authorize silently defaulting a setup value. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_DEFAULTS | step | 40 | apply_default | passed->AUTO_DESIGN | AUTO_LOOKUPS | stop | Task validation before any Data Loader handoff |

## Evidence

| Source ID | Source | Location | Revision boundary | Status |
|---|---|---|---|---|
| SRC-ORG-AMIMPL | ExpenseOrgSettingServiceAMImpl.java | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/expenseOrgSettingService/applicationModule/ExpenseOrgSettingServiceAMImpl.java | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; source snapshot hash in evidence/classic/manifest.json; reviewed 2026-10-09 | Confirmed |
| SRC-OPTION-AMIMPL | ExpenseSetupOptionServiceAMImpl.java | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/expenseSetupOptionService/applicationModule/ExpenseSetupOptionServiceAMImpl.java | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; source snapshot hash in evidence/classic/manifest.json; reviewed 2026-10-09 | Confirmed |
| SRC-UI-OPTIONS-AMIMPL | FinExmSetupOptionsAMImpl.java | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/exm/setup/options/model/src/oracle/apps/financials/expenses/setup/options/uiModel/applicationModule/FinExmSetupOptionsAMImpl.java | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; index 2026-10-09 08:42 GMT | Confirmed |
| SRC-ALM-REPORT-FETCH | ExpenseReportDataFetcher.java | https://alm.oraclecorp.com/fusionapps/#projects/erpm/scm/erp_core_expenses_integration.git/blob/src/main/java/oracle/apps/micro/fin/erpexpenses/app/expensereport/submit/util/ExpenseReportDataFetcher.java?revision=main | main; last-file-commit 88b0daec39c74c5656bffd225943f5565a4a8167 | Confirmed |

## Organization-setting profile

Use [the shipped transport profile](../references/fsm-transport-profile.md) for
organization-only writes and its documented source and verified-import boundaries. It
requires no customer-provided import ZIP. Other operations keep their explicit
qualification checks.
