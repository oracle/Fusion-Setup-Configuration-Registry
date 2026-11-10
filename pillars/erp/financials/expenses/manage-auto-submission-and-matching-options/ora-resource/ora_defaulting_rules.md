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

Maintainer provenance IDs: `SRC-ORG-AMIMPL`, `SRC-OPTION-AMIMPL`, `SRC-UI-OPTIONS-AMIMPL`, `SRC-ALM-REPORT-FETCH`.

The reusable contract is the task-local field, scope and package rules. Maintainer source locations are excluded from distribution and are not runtime inputs. Historical review does not qualify a new target or authorize an import. Retain every current-target and approval check.

## Organization-setting profile

Use [the shipped transport profile](../references/fsm-transport-profile.md) for
organization-only writes and its documented source and verified-import boundaries. It
requires no customer-provided import ZIP. Other operations keep their explicit
qualification checks.
