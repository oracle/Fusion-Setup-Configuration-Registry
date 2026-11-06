# Dependency readiness

These rules are reusable across target environments. Planner readiness means the execution rules are defined; all applicable runtime checks must still pass. The portable execution contract in ../references/execution-contract.md defines environment selection, input mapping, FSM compatibility checks and the in-memory Data Loader handoff. A missing product qualification is an explicit runtime blocker, never implicit approval.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Exact environment and scope | Use the latest explicitly selected environment; a supplied BU establishes BU-scoped modify intent. Missing or conflicting scope requires clarification. |
| 2 | Task ownership and code domains | Close the task-owned row/operation matrix and value contracts before preparing candidate rows. |
| 3 | Business-unit and import context | Use the source-backed FSM resolution contract only through the governed executor; qualify candidate scope markers. |
| 4 | Runtime readiness | Require complete registry, candidate validation and Data Loader preview/approval. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| bu_existence | Business unit exists and is usable | Conditional | BU-specific request | Verify | Repository Manage Business Unit lookup contract bound to the shared REST client in verify_business_unit_exists; verify target visibility at runtime | verify_business_unit_exists | Modification requires verified BU existence, separate from expense settings-row existence | Confirmed absence returns to the Run Book for the SKILL.md missing-BU prompt and owning task route; other failures retain their actual classification | Verified existence outcome and usable identity, or explicit blocker |
| bu_identity | Business-unit import context | Conditional | BU-specific request | Verify | Server-owned authenticated tenant/session context in both service import hooks; verify environment and BU through the selected workflow | resolve_business_unit | Names are tenant-context keys; EnterpriseId is resolved by the server and is not a workbook or public-LOV input | Preserve the verified BU and environment; do not infer global scope or substitute LOV identity for tenant-aware import resolution | Correct target authentication, unique verified BU and successful server-side scope resolution; never supply a guessed EnterpriseId |
| task_ownership | Entity and row ownership | Yes | Create or update | Verify | Reviewed control mappings and source-backed field roles: EXM_ORG_SETTING owns schedule/matching; EXM_SETUP_OPTION owns ENABLE_AUTO_SUB_DA_EXP; cash-advance alias has no independent editable task fields | qualify_fsm_transport | Shared aliases can suppress the intended rows | Evaluate target metadata and qualified transport profile; stop on FSM_ALIAS_COLLISION or FSM_SERIALIZATION_UNQUALIFIED | Exact code/scope rows; operation inserts or updates only those expense settings through their alternate key |
| feature_context | Feature-specific prerequisites | Conditional | User requests Agent deployment, merchant list editing or controls beyond the reviewed mappings | Verify | Requested control list checked against scripts/input_contract.py; this task changes reviewed settings only | resolve_feature_scope | Setting values do not enable or provision unrelated features | Return FEATURE_CONTRACT_REQUIRED with the requested feature and route to its owner; no such request means not applicable | Explicit applicable or not-applicable outcome; never infer a feature opt-in |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Blocked | Unknown ownership, scope, feature prerequisite or resolver contract | No. Preserve blocker and stop. |
| Satisfied | Verified evidence applicable to the exact environment and request | Only the operation declared by the active workflow; no prerequisite creation inferred. |

## Unresolved product and qualification dependencies

This checklist summarizes existing blockers; it does not define new lookup operations or replace the canonical rules. Resolve only the dependencies applicable to the requested operation, preserve source IDs and field dispositions, and recompile the registry after evidence-backed changes.

| Dependency | Current evidence boundary | Evidence needed to close the gap | Owning resource |
|---|---|---|---|
| Additional task controls beyond the reviewed mappings | Schedule and matching controls now have exact source-backed code mappings. | Map any additional requested control from its UI/AM source; do not expand to the shared EO list. | ora_reference_lookups.md, resolve_setting_code |
| Per-code setting values | Exact HH:mm and integer tolerance constraints plus runtime weekday codes are confirmed. System enable/weekday/direction enum domains are now confirmed. Target time-zone membership, extensible merchant selection when requested and complete FSM qualification remain unresolved. | Per-code import mapping, target acceptance of source-backed Etc/GMT+8 or another explicitly requested zone, qualified merchant lookup if requested, decoded-value behavior and justified default rules. | ora_reference_lookups.md, resolve_setting_value; ora_defaulting_rules.md |
| Entity and shared alias ownership | EXM_SETUP_OPTION and EXM_CASH_ADV_SETUP_AND_POLICY share a service/XML node; both header-only members are safe for organization-only changes; populated alias selection still needs qualification. | Source-backed entity/row/operation matrix and preservation rules for the shared package member. | ora_design_enforcement.md |
| Create/update and blank/null handling | Source-level create/update field roles, readXML audit rejection, decoded projection, and server-owned enterprise context are confirmed. Organization-only serialization uses the release-independent org-settings-schema-v1 contract. Exact fresh-target schema checks are required; release labels are diagnostic only. Historical four-row BU/global import evidence remains separate from verification of a new target. | Profile/schema compatibility and target checks; populated shared-alias selection remains unresolved. Live results require the normal status/reconciliation workflow. Do not reopen confirmed field roles as missing user inputs. | ora_input_validation.md; ora_design_enforcement.md |
| BU/global scope and deployment qualification | FSM Name-plus-EnterpriseId resolution and helper methods are confirmed source mechanisms. The server supplies tenant identity; target BU visibility and profile/schema compatibility must be verified; the shipped profile documents the source and verified-import boundaries for global rows. | Intended BU/global scope, candidate-specific identity checks through the selected workflow, and evidence applicable to the deployed framework revision. | ora_reference_lookups.md, resolve_business_unit |
| Feature-specific prerequisites | Release-qualified Expense Assistant evidence exists; it does not automatically qualify Expenses Agent behavior. | Matching release/feature prerequisites when that feature is requested; retain rejected rolling-document authority decisions. | Dependency Rules, feature_context |

MigratorHelper readXML, updatePrimaryKeysInXML and findByAltKey are no longer missing source dependencies. Their source mechanisms remain confirmed; this does not establish deployment parity or complete task behavior. See the framework evidence in ora_reference_lookups.md and ora_error_handling.md.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_DEPENDENCIES | step | 20 | resolve_dependency | passed->AUTO_LOOKUPS | AUTO_VALIDATE | stop | Task validation before any Data Loader handoff |

## Evidence

| Source ID | Source | Location | Revision boundary | Status |
|---|---|---|---|---|
| SRC-HELP-26D | Set up Expense Assistant | https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/set-up-expense-assistant.html | 26D | Confirmed |
| SRC-BO-SEEDS-COMPLETE | SetupBusinessObjectSD.xml | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/fun/db/data/FinFunShared/SetupBusinessObjectSD.xml | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; index 2026-10-09 | Confirmed |
| SRC-ORG-AMIMPL | ExpenseOrgSettingServiceAMImpl.java | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/expenseOrgSettingService/applicationModule/ExpenseOrgSettingServiceAMImpl.java | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; source snapshot hash in evidence/classic/manifest.json; reviewed 2026-10-09 | Confirmed |
| SRC-OPTION-AMIMPL | ExpenseSetupOptionServiceAMImpl.java | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/expenseSetupOptionService/applicationModule/ExpenseSetupOptionServiceAMImpl.java | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; source snapshot hash in evidence/classic/manifest.json; reviewed 2026-10-09 | Confirmed |
| SRC-BU-PEO | BusinessUnitPEO.xml | https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/hcm/components/hcmCoreSetup/organizations/fun/businessUnits/publicEntity/src/oracle/apps/financials/commonModules/businessUnits/publicEntity/BusinessUnitPEO.xml | FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64; index 2026-10-09 20:00:03 UTC | Confirmed |

Source-domain gaps closed on 2026-10-12: enable Y/N, seven weekday codes and three direction codes from complete System seed parents. The time-zone owning VO is identified; the source-backed fixed UTC−08:00 code is Etc/GMT+8, while target membership is still unresolved. See ora_reference_lookups.md for source URLs and boundaries.

Customers provide environment and business input only. The workflow obtains its
own template and baseline. The maintained transport profile, not a prior
customer import ZIP, supplies reusable serialization guidance.
