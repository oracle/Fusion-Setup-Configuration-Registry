# Design enforcement

These rules are reusable across target environments. Planner readiness means the execution rules are defined; all applicable runtime checks must still pass. The portable execution contract in ../references/execution-contract.md defines environment selection, input mapping, FSM compatibility checks and the in-memory Data Loader handoff. A missing product qualification is an explicit runtime blocker, never implicit approval.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-evidence-unresolved-operations:  -->

Supported create/update operations are bounded to organization-setting rows
under the shipped transport profile. A required setup-option write remains
blocked by FSM_ALIAS_COLLISION; these markers do not waive that check.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Task ownership | Prove exact rows and operations belong to this task. |
| 2 | Value and lifecycle contracts | Resolve applicable field and dependency blockers. |
| 3 | Governed handoff | Require current ready plan before handing validated intent to Data Loader. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any candidate package | Error | qualify_fsm_transport | Requested rows exceed the reviewed control mapping, or qualify_fsm_transport fails | Keep EXM_CASH_ADV_SETUP_AND_POLICY visible as a shared alias; do not edit cash-advance settings or assume its duplicate rows can be dropped | No inferred fix |
| Organization setting intent | Error | resolve_setting_code | Requested control is absent from the reviewed mapping, or proposed code conflicts with that mapping | Resolve each requested control to its exact owned code; retain an authoring gap for additional controls | No |
| Option or auto-submission intent | Error | resolve_auto_submission_value | ValueCode is outside the confirmed System enum Y/N | Use the explicit Yes/Y or No/N mapping; never turn blank into No | No |
| Create or update requested | Error | qualify_fsm_transport | Runtime template/alias/serialization checks have not passed | Preserve operation intent and return the exact compatibility error; no readiness override can supply missing product evidence | No |
| Request to edit an audit or identity field as a business value | Error |  | Audit edits or cross-scope identity ambiguity | Stop and correct the request; readiness override cannot authorize unsafe keys, audit edits or ownership bypass | No |
| Receipt/card matching setup | Error |  | A category or merchant matching change requests BU-only scope, or global scope has not been explicitly selected | SRC-HELP-26D defines matching as global only. Explain the impact and ask whether to apply globally or leave matching unchanged; do not reinterpret a BU request | No |
| Runtime or package handoff | Error | qualify_fsm_transport | Any applicable rule failed or lacks its required evidence | Return the exact runtime blocker and next action; authored planner readiness never waives product qualification | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_setting_code | Setting code selection | Exact control, owned SettingCode and scope from Reviewed control mappings | ora_reference_lookups.md |
| resolve_auto_submission_value | Auto-submission value selection | Exact Y/N from confirmed System seeds; no blank default | ora_reference_lookups.md |
| qualify_fsm_transport | Before composition and every handoff | Exact task/schema, deterministic alias selection, and applicable serialization evidence | ora_reference_lookups.md |

## Shared package boundary

The same-task metadata includes EXM_ORG_SETTING.csv, EXM_SETUP_OPTION.csv, and EXM_CASH_ADV_SETUP_AND_POLICY.csv. The latter two reference the same service/XML node. This proves a shared package relationship, not independent operation ownership, safe row duplication, or safe removal. Oracle FSM guidance requires retaining every CSV member and allows unselected business-object files to retain their headers with no data rows. Keep that general rule distinct from this shared-alias collision: the task-specific transformation/order behavior still needs qualification before constructing candidate rows. The selected task alias is EXM_SETUP_OPTION, as explained below. Never duplicate broad setup-option rows as a workaround.

### Applicability: no setup-option changes

Use the fresh same-target baseline and `split_verified_noops` to retain controls already satisfied in the result, without rewriting them. If only EXM_ORG_SETTING changes remain, both setup-option CSVs stay header-only and alias selection is not applicable. Header-only setup-option members contribute no requested writes in the organization-only profile. This does not qualify populated aliases. Apply all remaining transport checks.

### Selected alias and exact remaining dependency

The captured template has three business-object CSV descriptions, but only `EXM_ORG_SETTING` and `EXM_SETUP_OPTION` have migration-object rows with `MigrateFlag=Y`. Select **`EXM_SETUP_OPTION`** as the task alias; do not ask the user to choose again. This follows the migration-object selection in the captured task metadata and the user authorization to use either alias. Both setup-option aliases have `/SetupOptionVO/SetupOptionVORow` and `NodeSequence=1`. This selection expresses task intent; it does not establish that the framework excludes the other alias during transformation.

Populated setup-option aliases remain subject to `FSM_ALIAS_COLLISION`. Neither ZIP order, metadata order, business-object names nor migration flags establish deterministic selection. Header-only siblings must not be assumed harmless when another alias is populated.

Organization-only writes use the shipped [transport profile](../references/fsm-transport-profile.md). For populated option aliases, require the declared qualification workflow and successful import/read-back evidence of exactly the requested OptionCode and BuName, including audit/global serialization and preservation. Do not manufacture qualification from a local simulation.

Retain every original CSV and metadata member. Do not submit a customer package based on an assumed order, edit metadata to force a winner, or duplicate values across aliases as an unqualified workaround. Identical field/value maps in both aliases would make the reviewed collision order-independent in a local model, but this is not by itself a qualified end-to-end FSM import contract. Preserve this distinction and do not silently convert that inference into supported behavior.

The explicit maintainer branch in [option-alias qualification](../references/option-alias-qualification.md) permits testing the implemented identical-row candidate on a user-selected non-production target. This branch evaluates candidate conformance, exact test intent and ordinary target/approval gates; it does not assert customer transport qualification. Record that boundary in Task Hook results. Every other dependency and rule remains mandatory, with no readiness override. Reusable customer promotion requires the declared successful import/read-back evidence for the tested scope and operation.

Target framework compatibility must be verified. Alias names are business-object metadata, not environment aliases; validate runtime metadata against the selected target.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_DESIGN | step | 50 | design_enforcement | passed->AUTO_HANDOFF | AUTO_DEFAULTS | stop | Task validation before any Data Loader handoff |

## Evidence

Maintainer provenance IDs: `SRC-FSM-TEMPLATE`, `SRC-BO-SEEDS-COMPLETE`, `SRC-ORG-VO`, `SRC-OPTION-VO`, `SRC-UI-DA-PAGE`, `SRC-FSM-CSV-TRANSFORM`.

The reusable contract is the task-local field, scope and package rules. Maintainer source locations are excluded from distribution and are not runtime inputs. Historical review does not qualify a new target or authorize an import. Retain every current-target and approval check.



## Organization-setting profile

Use [the shipped transport profile](../references/fsm-transport-profile.md) for
organization-only writes and its documented source and verified-import boundaries. It
requires no customer-provided import ZIP. Other operations keep their explicit
qualification checks.
