# Manage Invoice Holds and Releases — Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-update-fields: AP_HOLD_CODE::UserUpdateableFlag, AP_HOLD_CODE::ExternalDescription, AP_HOLD_CODE::HoldInstruction, AP_HOLD_CODE::WaitBeforeNotifyDays, AP_HOLD_CODE::ReminderDays, AP_HOLD_CODE::InitiateWorkflowFlag, AP_HOLD_CODE::UserReleaseableFlag, AP_HOLD_CODE::InactiveDate, AP_HOLD_CODE::PostableFlag, AP_HOLD_CODE::DspDescription -->

This file owns operation scope, update restrictions and pre-import field
combinations for AP_HOLD_CODE setup definitions. Use [Input Validation](ora_input_validation.md)
for field/package rules, [Defaulting Rules](ora_defaulting_rules.md) for create
defaults, [Reference Lookups](ora_reference_lookups.md) for identity/description
dependencies, and [Error Handling](ora_error_handling.md) for execution and recovery.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AP_HOLD.DESIGN | step | 50 | design_enforcement | success->AP_HOLD.GATE;failure->AP_HOLD.ERRORS | AP_HOLD.DEFAULTS | stop | Setup-definition mutation intent |

## Operation Support

| Operation | Disposition |
|---|---|
| Create | Supported after input, default, identity and pre-import consistency checks. |
| Update | Supported fields: UserUpdateableFlag, ExternalDescription, HoldInstruction, WaitBeforeNotifyDays, ReminderDays, InitiateWorkflowFlag, UserReleaseableFlag, InactiveDate, PostableFlag and DspDescription. Apply the restrictions below. |
| End-date | An InactiveDate update, not a separate operation alias. It does not release transactional holds or qualify boundary-day behavior, reactivation or cleanup success. |
| Delete | Persisted deletion is unsupported (AP_NO_DELETE); removing NEW/INITIALIZED objects does not grant persisted-delete permission. Create has no reverse-delete rollback. |
| Apply or release a transactional invoice hold | Outside setup-definition scope; use the owning transaction workflow. Public invoiceHolds is not setup-definition CRUD. |

Reject unsupported scope and conflicting values before build; never silently
convert operations or replace supplied values. This node validates only.
Execution, approval, conditional reconciliation and recovery follow Error Handling.
Update Restrictions and Pre-import Consistency Rules are task-enforced policies;
they do not claim independent native importer rejection.

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Identity preflight fails | Error | find_hold_code_identity | Operation-specific exact-key contract fails. | Apply Record Identity in Reference Lookups; no implicit task-row upsert. | No |
| Existing key or type changes | Error |  | Requested HoldLookupCode or HoldType differs from the existing definition. | Preserve both; seed registration does not grant rename/type-change permission. | No |
| Audit values are supplied | Error |  | An audit field is treated as business input. | Apply audit ownership in Input Validation. | No |
| Description contract fails | Error | resolve_hold_description | Required description input or supporting dependency fails. | Apply Input Validation, Reference Lookups and the update restriction below; no standalone lookup mutation. | No |
| Nonseed create uses ORA_ prefix | Error |  | Name starts with ORA_, case-insensitively. | Request another key; do not invent seed or tag eligibility. | No automatic renaming |
| Routing Y with manual release N | Error |  | Final merged row has InitiateWorkflowFlag=Y and UserReleaseableFlag=N, except exact HoldLookupCode INCOMPLETE INVOICE. | Reject with AP_HOLD_RES_ROUTING_NO. The exception tests the name, not HoldType, and does not waive pre-import consistency. | No |

## Update Restrictions

After input shape and field-domain checks, evaluate update eligibility before
field combinations, dependent-value derivation or proposed corrections. Screen
restrictions associated with the stated type early; if the current baseline is
unavailable, disclose the restriction and leave actual change eligibility pending.

A change is an explicitly supplied value that differs from the baseline export.
Omission and valid same-value inputs are not changes. Compare InactiveDate by
calendar value and descriptions as exact strings without trimming or rewriting.

Use existing baseline flags for updateability and manual-release eligibility.
For routing details, use the requested InitiateWorkflowFlag when supplied;
otherwise use its existing value. Validate eligibility of any routing change
before checking its details. A blank InitiateWorkflowFlag, whether retained from
the export or explicitly cleared in the request, must not be treated as Y and
does not permit routing-detail changes. Preserve
the raw export value when routing is omitted; this interpretation does not
rewrite the CSV or enable routing. An eligible explicit Y can enable routing
and permit detail changes in the same request.
These rules apply to actual requested changes, including recovery updates;
derived omitted values are not explicit requests.

| Field | Reject a change when |
|---|---|
| PostableFlag or UserReleaseableFlag | HoldType is one of the five release types below, regardless of updateability. For every other type, baseline UserUpdateableFlag must be Y. |
| InitiateWorkflowFlag | Baseline UserReleaseableFlag or UserUpdateableFlag is exactly N. No direct HoldType condition. |
| WaitBeforeNotifyDays, ReminderDays or HoldInstruction | Baseline UserUpdateableFlag is N, or effective routing is N or blank. When routing is exactly N, explicit clears are allowed if baseline updateability permits; nonblank values are invalid. Derived routing-off cleanup follows the consistency rule below. No direct HoldType condition. |
| InactiveDate | Baseline UserUpdateableFlag is exactly N, including assignments or clears. No HoldType or manual-release condition. |
| DspDescription | Baseline UserUpdateableFlag is exactly N, regardless of HoldType. This does not restrict the separate ExternalDescription field. |

The five release types are:

- HOLD QUICK RELEASE REASON
- INV QUICK RELEASE REASON
- INVOICE RELEASE REASON
- MATCHING RELEASE REASON
- VARIANCE RELEASE REASON

Business labels map to these codes in [Type Labels](ora_reference_lookups.md#type-labels).
Changing UserUpdateableFlag does not clear dependent fields or grant eligibility
to another change in the same request. An eligible change to InitiateWorkflowFlag=Y
allows routing details to be changed in that request. Preserve omitted details
unless the routing-off or manual-release consistency rule below requires clearing.

## Pre-import Consistency Rules

Check these combinations before build and independently during candidate
validation, including any selected recovery stage.

| When the rule applies | Required values | Omitted values |
|---|---|---|
| Create with UserReleaseableFlag=N, or an eligible update changing it to N from Y or a blank baseline | InitiateWorkflowFlag=N; HoldInstruction, WaitBeforeNotifyDays and ReminderDays blank. | Derive only omitted outcomes as sourceDrivenEffects, separately from defaults. |
| Final InitiateWorkflowFlag=N on create or update, including unchanged or omitted routing on an existing N row | HoldInstruction, WaitBeforeNotifyDays and ReminderDays must all be blank. Reject supplied nonblank values, including unchanged values and zero days; accept eligible explicit clears. | Clear omitted resolution options as sourceDrivenEffects and show all three clears in the preview. This cleanup does not change the routing flag or bypass eligibility for an explicit routing change. |
| Create with one of the five release types above | UserReleaseableFlag=N; PostableFlag=N. Y is invalid for either flag, and requested PostableFlag X is outside the input domain. This is not an exhaustive HoldType allowlist. | Manual release remains explicit and required; omitted PostableFlag uses its create default N. |

For the manual-N rule, supplied routing Y or a routing clear conflicts with N.
Null or exact empty string clears optional instruction/day fields; instruction
whitespace and numeric days, including 0, are not blank. Reject conflicts using
the diagnostics in Error Handling.

An unchanged or omitted manual flag does not activate the manual-release rule.
The routing-off rule still clears resolution options whenever final routing is N.
A blank routing flag is not Y; preserve its raw value and apply the existing
detail restrictions without treating it as an explicit N cleanup trigger.

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| find_hold_code_identity | Create or update identity preflight | Operation-specific exact key. | ora_reference_lookups.md |
| resolve_hold_description | Requested or preserved complete-row description | Required description and supporting maintenance contract. | ora_reference_lookups.md |

## Import Processing

Every full-row update with a nonnull description performs supporting lookup
maintenance, including unchanged or preserved descriptions. Disclose it separately
from requested text changes; follow Reference Lookups and
[Importer Contract](ora_dependency_readiness.md#importer-contract).

Lookup maintenance and accounting processing add no customer inputs, hidden-state
proof or routine post-import verification. A valid candidate does not establish
saved values. Recovery does not guarantee hidden lookup or all-language restoration.

## Accounting Effects

An actual PostableFlag update reevaluates matching invoices with unreleased holds;
create and unchanged assignments do not trigger this hook. Show accountingEffects
in the preview without requiring an affected-invoice inventory or saved-state proof.

Reevaluation considers existing INCOMPLETE/UNPROCESSED invoice events and related
payment events when distribution event IDs exist. Distribution readiness and
remaining unreleased holds determine whether eligible events become UNPROCESSED
or remain INCOMPLETE. N or an existing persisted X can prevent completion, and Y does not bypass other
holds or distribution checks. A setup flag change
does not release a transactional hold or reverse an already-accounted transaction.

An eligible reverse flag update runs reevaluation again; it does not restore prior
accounting-event states or guarantee transaction rollback. Follow Error Handling
for conditional diagnostics and recovery.
